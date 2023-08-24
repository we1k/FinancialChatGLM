import os
import sys
import json
import shutil
import pandas as pd

from verbaliser import make_label

def double(df, row=0, column=2):
    # if len(df.index) != 1:
        # print(df)
        # raise KeyError('df more than 1 row')
    replace_list = ['(', ')', ' ', ',']
    if isinstance(df.iloc[row, column], str):
        for item in replace_list:
            df.iloc[row, column] = df.iloc[row, column].replace(item, '')
        return float(df.iloc[row, column])
    else:
        return df.iloc[row, column]
    
def Int(str):
    return int(str.replace(',', ''))

def Float(str):
    return float(str.replace(',', ''))
    
def contain_table(table_name, file_paths):
    path_list = []
    for path in file_paths:
        if table_name in path:
            path_list.append(path)
    return path_list

def search_json(company_name, date, key):
    dir_name = f"data/tables/{company_name}__{date}年"
    if not os.path.exists(dir_name):
        raise KeyError(f'{dir_name} dir not exists')
    
    file_path = os.path.join(dir_name, '基本信息表.json')
    basic_info_dict = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        basic_info_dict = json.load(f)

    return basic_info_dict[key]
    
def search_table(company_name, date, key):
    dir_name = f"data/tables/{company_name}__{date}年"
    if not os.path.exists(dir_name):
        raise KeyError(f'{dir_name} dir not exists')
    
    file_paths = os.listdir(dir_name)
    file_path = []
    
    if key in ['股本', '负债合计', '应付职工薪酬', '资产总计', '衍生金融资产', '应收款项融资', '其他非流动金融资产', '货币资金', '固定资产', '无形资产', '流动资产合计', '流动负债合计', '存货', '非流动资产合计',
    '交易性金融资产', '应收账款', '预付款项', '应付账款', 
    '其他非流动资产', '短期借款', '在建工程', '资本公积',
    '盈余公积', '未分配利润', '递延所得税负债']:
        file_path = contain_table('合并资产负债表', file_paths)
        if len(file_path) == 0:
            raise KeyError(f'{dir_name}/合并资产负债表.csv not exists')
    
    elif key in ['营业利润', '营业成本', '营业收入', '利息支出', '利息收入', '营业外支出', '营业外收入', '投资收益', '变动收益', '销售费用', '管理费用', '财务费用', '研发费用', '净利润', '综合收益总额', '税金及附加',  '利润总额', '所得税费用', '联营企业和合营企业投资收益', '投资收益', '利息收入', '投资收益', '公允价值变动收益',
    '信用减值损失', '资产减值损失', '资产处置收益', '综合收益总额',
    '持续经营净利润', '营业总收入', '营业总成本']:
        if key == '联营企业和合营企业投资收益':
            key = '联营企业和合营企业的投资收益'

        file_path = contain_table('合并利润表', file_paths)
        if len(file_path) == 0:
            raise KeyError(f'{dir_name}/合并利润表.csv not exists')
        
    elif key in ['现金及现金等价物余额', '期末现金及现金等价物余额', '现金及现金等价物净增加额', '收回投资收到现金', '投资支付', '经营活动现金流入', '经营活动现金流出',
    '投资活动现金流入', '投资活动现金流出', '筹资活动现金流出',
    '筹资活动现金流入', '各项税费']:
        if key == '现金及现金等价物余额': key = '期末现金及现金等价物余额'
        if key == '收回投资收到现金': key = '收回投资收到的现金'
        file_path = contain_table('合并现金流量表', file_paths)
        if len(file_path) == 0:
            raise KeyError(f'{dir_name}/合并现金流量表.csv not exists')
    
    df = None
    if len(file_path) == 0: return None
    elif len(file_path) == 1:
        file_path = os.path.join(dir_name, file_path[0])
        df = pd.read_csv(file_path)
    elif len(file_path) > 1:
        df = pd.read_csv(os.path.join(dir_name, file_path[0]))
        for path in file_path:
            path = os.path.join(dir_name, path)
            tmp = pd.read_csv(path)
            if len(tmp.index) > len(df.index):
                df = tmp
    
    # 清洗df 附注
    columns_to_drop = [col for col in df.columns if '附注' in col]
    df = df.drop(columns=columns_to_drop)
    
    def select_row(row):
        def vague_map(key, value):
            return any(key in value.replace(' ', '') if isinstance(value, str) else False for value in row.values)
        if isinstance(key, str):
            return vague_map(key, row.values)
        elif isinstance(key, list):
            return any(vague_map(k, row.values) for k in key)
        
    result_row = df[df.apply(select_row, axis=1)]
    # df = pd.DataFrame(result_row.values, columns=list(df.columns))
    if result_row.empty:
        raise KeyError('error dataframe empty')
    return result_row


def search_financial_key(key, stat_dict, company_name, date):
    if key == '每股收益':
        stat_dict['每股收益'] = Float(search_json(company_name, date, '每股收益'))
    
    elif key == '每股净资产':
        stat_dict['总股本'] = double(search_table(company_name, date, '股本'))
        stat_dict['净资产'] = Float(search_json(company_name, date, '净资产'))
        stat_dict['每股净资产'] = round(stat_dict['净资产'] / stat_dict['总股本'], 4)
        
    elif key == '每股经营现金流量':
        stat_dict['总股本'] = double(search_table(company_name, date, '股本'))
        stat_dict['现金流量净额'] = Float(search_json(company_name, date, '现金流量净额'))
        stat_dict['每股经营现金流量'] = round(stat_dict['现金流量净额'] / stat_dict['总股本'], 3)
        
    elif key == '负债合计':
        stat_dict[key] = search_table(company_name, date, key)
        stat_dict[key] = double(stat_dict[key], row=-1)

    elif key == '利息收入':
        stat_dict[key] = search_table(company_name, date, key)
        if len(stat_dict[key].index) > 0 and stat_dict[key].iloc[0, 0] < 10:
            stat_dict[key] = double(stat_dict[key], row=0)
        else:
            stat_dict[key] = None
    else:
        stat_dict[key] = double(search_table(company_name, date, key))

def parse_finacial(item):
    keys = item['task_key']
    stat_dict = {}
    company_name = item['Company_name']
    date = item['DATE'][0]
    for key in keys:
        try:
            search_financial_key(key, stat_dict, company_name, date)
        except Exception as e:
            # dir not found : 没有找到XXX的信息
            # keyerror: 没有找到XXX信息
            if 'dir' not in e.__repr__():
                print(item['question'], e)
            stat_dict[key] = '没有查询到对应的信息,无法回答'
        
    for k in stat_dict:
        stat_dict[k] = str(stat_dict[k])
    item['stat_dict'] = stat_dict
    
def parse_basic_info(item):
    if len(item['task_key']) == 1:
        key = item['task_key'][0]
    else:
        print(item)
        return 
    # assert , "Ratio key got more than one argument"
    company_name, date = item['Company_name'], item['DATE'][0]
    try:
        if key == '法定代表人是什么':
            ret = search_json(company_name, date, "法定代表人")
       
        elif key == '法定代表人是否相同':
            if item['DATE'][0] > item['DATE'][1]:
                item['DATE'][0], item['DATE'][1] = item['DATE'][1], item['DATE'][0]
            start_date, last_date = int(item['DATE'][0]), int(item['DATE'][1])
                
            cur_TL = search_json(company_name, start_date, "法定代表人")
            date = int(start_date) + 1
            ret_name = [cur_TL]
            ret = '相同'
            while date <= last_date:
                TL = search_json(company_name, date, "法定代表人")
                ret_name.append(TL)
                if TL != cur_TL:
                    ret = '不相同'
                    break
                date += 1
            ret = ret + '|' + ret_name[0] + '|' + ret_name[1]
        
        elif key == '企业名称':
            company_names_dict = {}
            with open('data/company_names.txt', 'r', encoding='utf-8') as f:
                for line in f.readlines():
                    name, short_name = line.strip().split(":")
                    company_names_dict[short_name] = name
            
            if company_name in company_names_dict:
                ret = company_names_dict[company_name]
            else:
                ret = '没有查询到对应的信息,无法回答'
        
        elif key == '证券简称':
            ret = company_name
            
        else:
            ret = search_json(company_name, date, key)
            
        if isinstance(ret, str):
            ret = ret.replace(',', '')
        
        if ret == '-1':
            ret = '没有查询到对应的信息,无法回答'
        
    except Exception as e:
        # 如果 dir not exist 无法回答
        # 如果json not exist 可能是解析失败
        if 'dir' not in e.__repr__():
            print(item['question'], e)
        ret = '没有查询到对应的信息,无法回答'
    
    ret = str(ret)
    item['stat_dict'] = {key: ret}
    
def parse_ratio(item):
    assert len(item['task_key']) == 1, "Ratio key got more than one argument"
    key = item['task_key'][0]
    company_name, date = item['Company_name'], item['DATE'][0]
    stat_dict = {}
    try:
        if key == '流动比率':
            stat_dict['流动资产'] = double(search_table(company_name, date, '流动资产合计'))
            stat_dict['流动负债'] = double(search_table(company_name, date, '流动负债合计'))
            ret = stat_dict['流动资产'] / stat_dict['流动负债']
            
        elif key == '速动比率':
            stat_dict['流动资产'] = double(search_table(company_name, date, '流动资产合计'))
            stat_dict['存货'] = double(search_table(company_name, date, '存货'))
            stat_dict['流动负债'] = double(search_table(company_name, date, '流动负债合计'))
            ret = (stat_dict['流动资产'] - stat_dict['存货']) / stat_dict['流动负债']
            
        elif key == '现金比率':
            stat_dict['货币资金'] = double(search_table(company_name, date, '货币资金'))
            stat_dict['流动负债'] =  double(search_table(company_name, date, '流动负债合计'))
            ret = stat_dict['货币资金'] /stat_dict['流动负债']
            
        elif key == '资产负债比率':
            stat_dict['总负债'] = double(search_table(company_name, date, '负债合计'), row=2)
            stat_dict['资产总额'] = double(search_table(company_name, date, '资产总计'))
            ret = stat_dict['总负债'] / stat_dict['资产总额']
            
        elif key == '毛利率':
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            stat_dict['营业成本'] = double(search_table(company_name, date, '营业成本'))
            ret = (stat_dict['营业收入'] - stat_dict['营业成本']) / stat_dict['营业收入']
        
        elif key == '净利润率':
            stat_dict['净利润'] = double(search_table(company_name, date, '净利润'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            ret = stat_dict['净利润'] / stat_dict['营业收入']
        
        elif key == '流动负债比率':
            stat_dict['流动负债'] = double(search_table(company_name, date, '流动负债合计'))
            stat_dict['总负债'] = double(search_table(company_name, date, '负债合计'), row=2)
            ret = stat_dict['流动负债'] / stat_dict['总负债']
        
        elif key == '非流动负债比率':
            stat_dict['非流动负债'] = double(search_table(company_name, date, '非流动负债合计'))
            stat_dict['总负债'] = double(search_table(company_name, date, '负债合计'), row=2)
            ret = stat_dict['非流动负债'] / stat_dict['总负债']
            
        elif key == '研发经费占费用比例':
            stat_dict['销售费用'] = double(search_table(company_name, date, '销售费用'))
            stat_dict['管理费用'] = double(search_table(company_name, date, '管理费用'))
            stat_dict['财务费用'] = double(search_table(company_name, date, '财务费用'))
            stat_dict['研发费用'] = double(search_table(company_name, date, '研发费用'))
            ret = stat_dict['研发费用'] / (stat_dict['销售费用'] + stat_dict['管理费用'] + stat_dict['财务费用'] + stat_dict['研发费用']) 
            
        elif key == '三费比重':
            stat_dict['销售费用'] = double(search_table(company_name, date, '销售费用'))
            stat_dict['管理费用'] = double(search_table(company_name, date, '管理费用'))
            stat_dict['财务费用'] = double(search_table(company_name, date, '财务费用'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            ret = (stat_dict['销售费用'] + stat_dict['管理费用'] + stat_dict['财务费用']) / stat_dict['营业收入']
            
        elif key == '财务费用率':
            stat_dict['财务费用'] = double(search_table(company_name, date, '财务费用'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            ret =  stat_dict['财务费用'] / stat_dict['营业收入']
            
        elif key == '管理费用率':
            stat_dict['管理费用'] = double(search_table(company_name, date, '管理费用'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            ret =  stat_dict['管理费用'] / stat_dict['营业收入']
        
        elif key == '营业成本率':
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            stat_dict['营业成本'] = double(search_table(company_name, date, '营业成本'))
            ret =  stat_dict['营业成本'] / stat_dict['营业收入']
            
        elif key == '营业利润率':
            stat_dict['营业利润'] = double(search_table(company_name, date, '营业利润'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            ret =  stat_dict['营业利润'] / stat_dict['营业收入']
        
        
        elif key.endswith('增长率'):
            if key == '现金及现金等价物增长率':
                _key = '期末现金及现金等价物余额'
            elif key == '流动负债增长率':
                _key = '流动负债合计'
            elif key == '总资产增长率':
                _key = '资产总计'
            elif key == '总负债增长率':
                _key = '负债合计'
            else:
                _key = key[:-3]
            
            search_result = search_table(company_name, date, _key)
            stat_dict['去年'] = double(search_result, column=3) 
            stat_dict['今年'] = double(search_result) 
            ret = stat_dict['今年'] / stat_dict['去年'] - 1
            
        elif key == '投资收益占营业收入比率':
            stat_dict['投资收益'] = double(search_table(company_name, date, '投资收益'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            
            ret = stat_dict['投资收益'] / stat_dict['营业收入']
            
        elif key == '研发经费与营业收入比值':
            stat_dict['研发费用'] = double(search_table(company_name, date, '研发费用'))
            stat_dict['营业收入'] = double(search_table(company_name, date, '营业收入'))
            
            ret = stat_dict['研发费用'] / stat_dict['营业收入']
        
        elif key == '研发经费与利润比值':
            stat_dict['研发费用'] = double(search_table(company_name, date, '研发费用'))
            stat_dict['净利润'] = double(search_table(company_name, date, '净利润'))
            ret = stat_dict['研发费用'] / stat_dict['净利润']
            
        elif key == '研发人员占职工人数比例':
            stat_dict['研发人员数'] = Int(search_json(company_name, date, '研发人员数'))
            stat_dict['职工总数'] = Int(search_json(company_name, date, '职工总数'))
            ret = stat_dict['研发人员数'] / stat_dict['职工总数'] if stat_dict['研发人员数'] != -1 and stat_dict['职工总数'] != -1 else -1
            if ret == -1:
                raise KeyError()
                # ret = '没有查询到对应的信息,无法回答'
                
        elif key == '硕士及以上人员占职工人数比例':
            stat_dict['硕士人数'] = Int(search_json(company_name, date, '硕士人数'))
            stat_dict['博士及以上'] = Int(search_json(company_name, date, '博士及以上'))
            if stat_dict['博士及以上'] == -1: stat_dict['博士及以上'] = 0
            stat_dict['职工总数'] = Int(search_json(company_name, date, '职工总数'))
            ret = (stat_dict['硕士人数'] + stat_dict['博士及以上']) / stat_dict['职工总数'] if stat_dict['硕士人数'] != -1 and stat_dict['职工总数'] != -1 else -1
            if ret == -1:
                raise KeyError()
                # ret = '没有查询到对应的信息,无法回答'
        else:
            print(item['question'])
            ret = 0
        
        if key in ['研发经费与利润比值', '研发经费与营业收入比值', '流动比率', '速动比率', '研发经费占费用比例', '硕士及以上人员占职工人数比例', '研发人员占职工人数比例']:
            ret = str(round(ret * 100, 2))
        else:
            ret = str(round(ret * 100, 2)) + '%'

    except Exception as e:
        if 'dir' not in e.__repr__():
            print(item['question'], e)
        ret = '没有查询到对应的信息,无法回答'
        stat_dict[key] = ''
    
    stat_dict[key] = str(ret)
    item['stat_dict'] = stat_dict
    

def parse_special(item):
    pass

def parse_analysis(item):
    pass


parse_fn_dict = {
    '0' : parse_special,
    '1' : parse_basic_info,
    '2' : parse_ratio,
    '3' : parse_finacial,
    '4' : parse_analysis,
}

def parse_question(path='./data/parse_question.json'):
    questions = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            questions.append(json.loads(line))
    
    datasets = []    
    for question in questions:
        parse_fn = parse_fn_dict[str(question['category'])]
        company_name = question['Company_name']
        year = question['DATE']
        parse_fn(question)

    make_label(questions)
    
    for question in questions:
        if question['prompt'] != '':
            datasets.append({
                "question" : question['question'],
                "prompt" : f"{question['prompt']}",
                "target" : f"{question['prompt']}",
                "category" : question['category'],
            })
        else:
            datasets.append({
                "question" : question['question'],
                "prompt" : f"简洁和专业的来回答用户的问题，如果无法从中得到答案，可以乱编或改写提问句子回复。无法根据以上信息回答问题",
                "target" : "无法根据以上信息回答问题",
                "category" : question['category'],
            })
            
        
    with open('data/dataset.json', 'w') as file:
        for question in questions:
            file.write(json.dumps(question, ensure_ascii=False) + '\n')
    
    with open('data/smp2023/dataset.json', 'w') as file:
        json.dump(datasets, file, ensure_ascii=False)

# puts into language model dataset

def reconstruct_dataset():
    results = []
    with open('data/result1.json', 'r', encoding='utf-8') as f1, open('data/dataset.json', 'r', encoding='utf-8') as f2:
        for line, answer in zip(f1.readlines(),f2.readlines()):
            result = json.loads(line)
            dataset = json.loads(answer)
            result['prompt'] = dataset['prompt']
            result['target'] = result['prompt']
            result['category'] = dataset['category']
            if result['prompt'] == '':
                result['target'] = result['answer']
                result['prompt'] = '没有查询到对应的信息'
            
            if result['target'] == "":
                result['target'] = "没有查询到对应的信息，根据以上信息无法回答"
            
            result.pop('id')
            result.pop('answer')
            results.append(result)
    
    with open('data/smp2023/dataset.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
        
if __name__ == '__main__':
    parse_question()