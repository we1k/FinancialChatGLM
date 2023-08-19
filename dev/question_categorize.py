import os
import re
import sys
import json
from collections import defaultdict

def has_digit(input_str):
    pattern = r'\d'  # 正则表达式匹配数字的模式
    return bool(re.search(pattern, input_str))

def has_keys(str, keys):
    for key in keys:
        if key in str:
            return True
    return False

#### 基本信息
##### 公司治理 , 董事、监事、高级管理人员和员工情况
basis_info_questions = defaultdict(list)
basis_info_keys = [
    '电子信箱', '企业名称', '办公地址', '注册地址', '外文名称', '证券简称',
    '法定代表人是什么', '证券代码', '公司网址', '法定代表人是否相同',
    '职工总数', '技术人员数', '博士及以上', '硕士人数', '研发人员数',
    
]
basis_info_keys.sort(key=lambda x:-len(x))

#### 财务报告
finacial_questions = defaultdict(list)
finacial_keys = [
    ## 财务报表
    # 合并资产负债表
    '负债合计', '应付职工薪酬', '资产总计', 
    '应收款项融资', '货币资金',
    '衍生金融资产和其他非流动金融资产', '衍生金融资产', '其他非流动金融资产',
    '固定资产和无形资产', '固定资产', '无形资产', '存货', '股本'
    #######
    '交易性金融资产', '应收账款', '预付款项', '应付账款', 
    '其他非流动资产', '短期借款', '在建工程', '资本公积',
    '盈余公积', '未分配利润', '递延所得税负债', 
    # 合并利润表 
    '营业利润', '营业成本', '营业收入', '营业成本和营业利润', 
    '营业外支出', '营业外收入',
    '利息支出和利息收入', '利息支出', '利息收入',
    '营业外支出和营业外收入',  '投资收益', '变动收益',
    '研发费用和财务费用', '研发费用', '财务费用', 
    '销售费用和管理费用', '销售费用', '管理费用', 
    '利润总额和净利润', '利润总额', '净利润', 
    '所得税费用', '综合收益总额', '税金及附加', 
    '联营企业和合营企业投资收益',
    ###########
    '投资收益', '利息收入', '投资收益', '公允价值变动收益',
    '信用减值损失', '资产减值损失', '资产处置收益', '综合收益总额',
    '持续经营净利润', '营业总收入', '营业总成本',
    # 合并现金流量表
    '收回投资收到现金', '现金及现金等价物余额', 
    '投资支付', '经营活动现金流入', '经营活动现金流出',
    '投资活动现金流入', '投资活动现金流出', '筹资活动现金流出',
    '筹资活动现金流入', '现金及现金等价物净增加额', '各项税费'
    # 总股本/总股数
    ### unrecog #找出总股数，计算得到  净资产 / 普通股总数, '营业总成本'
    '每股收益和每股净资产', '每股净资产', '每股经营现金流量',
]
finacial_keys.sort(key=lambda x:-len(x))
### 可能包含多个章节
analysis_questions = defaultdict(list)
analysis_keys = [
    '报告期内公司环境信息', '主要销售客户集中度', '供应商情况', '控股股东及实控人', '董事、监事、高级管理人员报酬', '研发投入情况', '审计意见情况', '聘任、解聘会计师事务情况', '主要供应商情况', '重大关联交易情况', '社会责任工作情况', '营业收入构成整体情况', '现金流量净额变动原因' ,
    '营业收入变动情况及原因', '投资收益变动原因',
    '分析', '情况', '原因', '简要介绍', '简要概述',
]
analysis_keys.sort(key=lambda x:-len(x))

# 需要计算的统计量
ratio_questions = defaultdict(list)
ratio_keys = [
    '流动比率', '速动比率', '现金比率', '资产负债比率',  '毛利率', '净利润率', '流动负债比率',
    '三费比重', '财务费用率', '管理费用率',
    # 
    '营业成本率', '营业利润率', 
    '现金及现金等价物增长率', '流动负债增长率',
    '总资产增长率', '总负债增长率', '货币资金增长率',
    '净利润增长率', '投资收益增长率',
    # 
    '管理费用增长率', '财务费用增长率', 
    '研发费用增长率', '销售费用增长率', 
    '无形资产增长率', '固定资产增长率', 
    '营业利润增长率', '营业收入增长率', 
    '投资收益占营业收入比率', '研发经费与营业收入比值', 
    '研发经费占费用比例',
    '研发经费与利润比值', 
    '研发人员占职工人数比例', '硕士及以上人员占职工人数比例',
    '比例', 
]
ratio_keys.sort(key=lambda x:-len(x))

# 公司未来发展的展望 在财务报告的最后！！！！
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
    '应付职工薪酬': ['职工薪酬总额'],
    '控股股东及实控人': ['控股股东及实际控制人'],
    '研发经费占费用比例': ['研发经费在费用', '研发经费占费用比例'],
    '研发经费与利润比值': ['研发经费与利润比例'],
    '研发经费与营业收入比值': ['研发经费与营业收入比例'],
    '研发人员占职工人数比例': ['研发人员在职工人数中占比例', '研发人员占职工总数人数比例', '研发人员占职工总数比例'],
    '硕士及以上人员占职工人数比例': ['硕士及以上员工占职工总数比例'],
    '客户' : ['客户客户'],
    '三费比重' : ['三费（销售费用、管理费用和财务费用）占比'],
    '每股收益和每股净资产' : ['每股收益以及每股净资产'],
    '投资收益占营业收入比率': ['投资收益占营业收入比例'],
    '收回投资收到现金' : ['收回投资所收到现金', '收回投资所得到现金'],
}

special_questions = []
unrecog_questions = []


def classify_questions(samples):
    for i in range(len(samples)):
        question = samples[i]['question'].replace('学历', '').replace('的', '').replace(' ', '').replace('所占', '占').replace('上费用', '费用').replace('总费用', '费用')
        question = re.sub(r'(\d+年)(法定代表人)(对比|与)(\d+年)', r'\1与\4\2', question)
        # print(question)
        if '法定代表人' in question and '相同' in question:
            question = question + '|法定代表人是否相同'
        
        samples[i]['prompt'] = ''
        if question.startswith("华天酒店2020年法定代表人对比2019年是否相同"):
            cnt = 1
        if isinstance(samples[i]['Company_name'], list):
            samples[i]['Company_name'] = ''
        for k, v in vague_mapping.items():
            for x in v:
                question = question.replace(x, k)
            
        if not has_digit(question):
            samples[i]['category'] = 0
            special_questions.append(samples[i])
            samples[i]['task_key'] = 'special'
                    
        elif has_keys(question, basis_info_keys):
            samples[i]['category'] = 1
            for key in basis_info_keys:
                if key in question:
                    basis_info_questions[key].append(samples[i])
                    break
            samples[i]['task_key'] = key
        
        
        elif has_keys(question, ratio_keys):
            samples[i]['category'] = 2
            for key in ratio_keys:
                if key in question:
                    ratio_questions[key].append(samples[i])
                    break
            samples[i]['task_key'] = key
        
        elif has_keys(question, finacial_keys):
            samples[i]['category'] = 3
            for key in finacial_keys:
                if key in question:
                    finacial_questions[key].append(samples[i])
                    break
            samples[i]['task_key'] = key
        
        elif has_keys(question, analysis_keys):
            samples[i]['category'] = 4
            for key in analysis_keys:
                if key in question:
                    analysis_questions[key].append(samples[i])
                    break
            samples[i]['task_key'] = key
        
        else:
            samples[i]['category'] = 0
            samples[i]['task_key'] = 'special'
            unrecog_questions.append(samples[i])


def main():
    samples = []
    path = 'data/questions/test.json'
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = json.loads(line)
            samples.append(line)

    classify_questions(samples)
    with open('data/questions/test.json', 'w', encoding='utf-8') as f:
        for sample in samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    main()