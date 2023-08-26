import os
import re
import sys
import json
from collections import defaultdict

import torch
from torch.utils.data import DataLoader, Dataset
import jieba
from fuzzywuzzy import process
from transformers import T5Config, T5Tokenizer, T5ForConditionalGeneration

from constant import CANDIDATE_KEY, RATIO_KEY, BASIC_KEY, FINANCIAL_KEY, ANALYSIS_KEY, VAGUE_MAPPING, KEY_REMAPPING

def has_digit(input_str):
    pattern = r'\d'  # 正则表达式匹配数字的模式
    return bool(re.search(pattern, input_str))

def has_keys(str, keys):
    for key in keys:
        if key in str:
            return True
    return False


special_questions = []
unrecog_questions = []


def verbaliser(_str):
    _str = _str.replace('的', '').replace(' ', '').replace('所占', '占').replace('上费用', '费用').replace('总费用', '费用').replace('学历', '').replace('以及', '和')
    _str = re.sub(r'(\d+年)(法定代表人)(对比|与)(\d+年)', r'\1与\4\2', _str)
    
    for k, v in VAGUE_MAPPING.items():
        for x in v:
            _str = _str.replace(x, k)
    return _str
    
class SMP_Dataset(Dataset):
    def __init__(self, samples, tokenizer, max_length) -> None:
        self.questions = [verbaliser(sample["question"]) for sample in samples]
        self.samples = [f"从输入中找出的金融指标名称。\n输入：“{input}”" for input in self.questions]
        self.tokenizer = tokenizer
        self.input_ids = tokenizer(self.samples, max_length=max_length, padding=True, truncation=True, return_tensors='pt')['input_ids']
    
    def __getitem__(self, index):
        return self.input_ids[index]
    
    def __len__(self):
        return len(self.samples)
        
def classify_questions(samples):
    model_path = "model/smp_question_clf/checkpoint-5000"
    #Load pretrained model and tokenizer
    config = T5Config.from_pretrained(model_path)
    tokenizer = T5Tokenizer.from_pretrained(model_path)
    model = T5ForConditionalGeneration.from_pretrained(model_path,config=config).cuda()
    model.resize_token_embeddings(len(tokenizer))
    model.eval()
    
    test_dataset = SMP_Dataset(samples, tokenizer, max_length=64)
    test_dataloader = DataLoader(test_dataset,batch_size=2048,shuffle=False)
    
    ret = []
    for batch in test_dataloader:
        batch = batch.cuda()
        
        logits = model.generate(
            input_ids=batch,
            max_length=20, 
            early_stopping=True,
        )

        logits=logits[:,1:]
        labels = tokenizer.batch_decode(logits, skip_special_tokens=True)
        ret += [[process.extractOne(word, CANDIDATE_KEY)[0] for word in label.split('和')\
            if process.extractOne(word, CANDIDATE_KEY)[1] > 65] \
            if '联营企业和合营企业投资收益' not in label \
            else [label] \
            for label in labels]
        
    for i, task_keys in enumerate(ret):
        if samples[i]['Company_name'] == '':
            task_keys = ['特殊问题']

        task_key_set = set()
        for key in task_keys:
            if key == "联营企业和合营企业投资收益":
                task_key_set.add(key)
            else:
                for item in key.split("和"):
                    task_key_set.add(item)
        task_keys = list(task_key_set)
        samples[i]['task_key'] = task_keys
        
        # didn't match a task key
        if len(task_keys) == 0:
            re_classify_question(samples[i])
            print(samples[i])
            continue
            
        if task_keys[0] in BASIC_KEY:
            samples[i]['category'] = 1
        elif task_keys[0] in RATIO_KEY:
            samples[i]['category'] = 2
        elif task_keys[0] in FINANCIAL_KEY:
            samples[i]['category'] = 3
        elif task_keys[0] in ANALYSIS_KEY:
            samples[i]['category'] = 4
        else:
            samples[i]['category'] = 0
    
        # key_remapping 
        for j, key in enumerate(samples[i]['task_key']):
            if key in KEY_REMAPPING:
                samples[i]['task_key'][j] = KEY_REMAPPING[key]

def re_classify_question(sample):
    question = verbaliser(sample['question'])
    # print(question)
    if '法定代表人' in question and '相同' in question:
        question = question + '|法定代表人是否相同'
    
    sample['prompt'] = ''
    if not has_digit(question):
        sample['category'] = 0
        special_questions.append(sample)
        sample['task_key'] = '特殊问题'
                
    elif has_keys(question, BASIC_KEY):
        sample['category'] = 1
        for key in BASIC_KEY:
            if key in question:
                break
        sample['task_key'] = key
    
    elif has_keys(question, RATIO_KEY):
        sample['category'] = 2
        for key in RATIO_KEY:
            if key in question:
                break
        sample['task_key'] = key
    
    elif has_keys(question, FINANCIAL_KEY):
        sample['category'] = 3
        for key in FINANCIAL_KEY:
            if key in question:
                break
        sample['task_key'] = key
    
    elif has_keys(question, ANALYSIS_KEY):
        sample['category'] = 4
        for key in ANALYSIS_KEY:
            if key in question:
                break
        sample['task_key'] = key
    
    else:
        sample['category'] = 0
        sample['task_key'] = '特殊问题'
        unrecog_questions.append(sample)

    sample['task_key'] = [sample['task_key']]
    

def main():
    samples = []
    path = 'data/parse_question.json'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = json.loads(line)
            samples.append(line)

    classify_questions(samples)
    with open('data/parse_question.json', 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    main()