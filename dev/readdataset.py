import json
import ast

with open('/home/lzw/project/langchain-ChatGLM/data/dataanswer.json','w') as f:
    pass

vague_mapping = {
    '法定代表人是否相同' : ['法定代表人相比相同吗', '法定代表人是否都相同', '法定代表人是否有都是相同'],
    '硕士人数': ['硕士员工人数', '硕士研究生员工数量'],
    '电子信箱': ['电子邮箱'],
    '是什么': ['是谁'],
    '法定代表人是什么': ['法定代表人。'],
    '简要概述': ['简述'],
    # '资产总计': ['资产总额'],
    '公司网址': ['网站'],
    '职工总数': ['总职工', '员工总数', '职工总人数'],
    '外文名称': ['英文名称'],
    '技术人员数': ['技术员工人数'],
    '企业名称': ['官方注册名称'],
    '利润比例': ['利润之比'],
    '利息支出': ['支出利息'],
    '研发费用': ['研发上费用'],
    '应付职工薪酬': ['薪酬总额'],
    '控股股东及实控人': ['控股股东及实际控制人'],
    '研发经费占费用比例': ['研发经费在总费用'],
    '研发经费与利润比例': ['研发经费与利润比值'],
    '研发人员占职工人数比例': ['研发人员在职工人数中占比例', '研发人员占总职工人数比例', '研发人员占职工总人数比例'],
    '硕士及以上人员占职工人数比例': ['硕士及以上学历员工占职工总数比例'],
    '客户' : ['客户客户'],
    '三费比重' : ['三费（销售费用、管理费用和财务费用）占比'],
    '每股收益和每股净资产' : ['每股收益以及每股净资产'],
    '研发经费与营业收入比例': ['研发经费与营业收入比值'],
}

for line in open('/home/lzw/project/langchain-ChatGLM/data/dataset.json','r',encoding='utf-8'):
    c = json.loads(line)
    question = c['question']
    prompt = c['prompt']
    index = prompt.find('{')
    if index == -1:
        answer = '无法根据以上信息回答问题'
    else:
        info = ast.literal_eval(prompt[index:])
        count = 0
        answer = ''
        for info_key in info.keys():
            info_value = info[info_key]
            flag = 0
            if '没有查询到对应的信息' in info_value:
                answer = answer + '没有查询到%s对应的信息'%(info_key)
            elif info_key in question:
                flag = 1
            elif vague_mapping.get(info_key):
                for it in vague_mapping[info_key]:
                    if it in question:
                        flag = 1
                        break
            if flag == 1:
                i = (question.find('是') == -1) and question.find('为') or question.find('是')
                answer = (count == 0) and question[:i + 1] + info_value or answer + '，%s'%(info_value)
            else:
                answer = '无法根据以上信息回答问题'
            count = count + 1
    with open('/home/lzw/project/langchain-ChatGLM/data/dataanswer.json', 'a+') as file:
        json.dump(dict(question = question, prompt = prompt, answer = answer), file, ensure_ascii=False)
        file.write('\r')