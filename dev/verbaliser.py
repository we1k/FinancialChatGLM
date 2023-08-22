import os
import sys
import json

ratio_key_dict = {
    "流动比率" : ["流动资产", "流动负债"],
    "净利润率" : ["净利润", "营业收入"],
    "资产负债比率" : ["总负债", "资产总额"],
    "现金比率" : ["货币资金", "流动负债"],
    "净利润率" : ["净利润", "营业收入"],
    "流动负债比率" : ["流动负债", "总负债"],
    "财务费用率" : ["财务费用", "营业收入"],
    "管理费用率" : ["管理费用", "营业收入"],
    "营业成本率" : ["营业成本", "营业收入"],
    "营业利润率" : ["营业利润", "营业收入"],
    "投资收益占营业收入比率" : ["投资收益", "营业收入"],
    "研发经费与营业收入比值" : ["研发费用", "营业收入"],
    "研发经费与利润比值" : ["研发费用", "净利润"],
    "研发人员占职工人数比例" : ["研发人员数", "职工总数"]
    # "速动比率" : ["", ""],
    # "毛利率" : ["", ""],
    # "研发经费占费用比例" : ["", ""],
    # "三费比重" : ["", ""],
    # 企业硕士及以上人员占职工人数比例
}

def make_label(samples):
    # according to keys
    for sample in samples:
        key = sample['task_key']
        company_name = sample['Company_name']
        date = sample['DATE']
        
        template = f'NOT implement'
        if "stat_dict" not in sample: continue
        stat_dict = sample['stat_dict']
        if stat_dict[key] == '没有查询到对应的信息,无法回答':
            continue
        # special question:
        if sample['category'] == 0:
            pass
        
        # basic info
        elif sample['category'] == 1:
            date = int(date[0])
            
            if key == '法定代表人是什么':
                template = f"{company_name}在{date}的法定代表人是{stat_dict[key]}"
                
            elif key == '法定代表人是否相同':
                ret = stat_dict[key].split('|')
                if ret[0] == '相同':
                    template = f"{company_name}在{date}与{date+1}的法定代表人是相同，法定代表人均是{ret[1]}"
                elif ret[0] == '不相同':
                    template = f"{company_name}在{date}与{date+1}的法定代表人是不相同的。在{date}的法定代表人是{ret[1]}，在{date+1}的法定代表人是{ret[2]}"
            else:
               template = f"{company_name}在{date}的{key}是{stat_dict[key]}"
            
        # ratio keys
        elif sample['category'] == 2:
            date = int(date[0])
            if key.endswith('增长率'):
                if key == '现金及现金等价物增长率':
                    _key = '期末现金及现金等价物余额'
                elif key == '流动负债增长率':
                    _key = '流动负债'
                elif key == '总资产增长率':
                    _key = '资产总额'
                elif key == '总负债增长率':
                    _key = '总负债'
                else:
                    _key = key[:-3]
                    
                template = f"{company_name}在{date-1}年的{_key}为{stat_dict['去年']}元，在{date}年的{_key}为{stat_dict['今年']}元，根据公式{key}=({_key}-上年{_key})/上年{_key}，得出{company_name}在{date}年的{key}是{stat_dict[key]}"
            
            elif key == '速动比率':
                template = f"{company_name}在{date}年的流动资产合计为{stat_dict['流动资产']}元，在{date}年的存货为{stat_dict['存货']}元，在{date}年的流动负债合计为{stat_dict['流动负债']}元，根据公式速动比率=(流动资产-存货)/流动负债,得出{company_name}在{date}年的速动比率是{stat_dict[key]}"
                
            elif key == '毛利率':
                template = f"{company_name}在{date}年的营业收入为{stat_dict['营业收入']}元，在{date}年的营业成本为{stat_dict['营业成本']}元，根据公式速动比率=(营业收入-营业成本)/营业收入,得出{company_name}在{date}年的毛利率是{stat_dict[key]}"
                
            elif key == '研发经费占费用比例':
                template = f"{company_name}在{date}年的研发费用为{stat_dict['研发费用']}元，销售费用为{stat_dict['销售费用']}元，财务费用为{stat_dict['财务费用']}元，管理费用为{stat_dict['管理费用']}元，根据公式，企业研发经费占费用比例=研发费用/(销售费用+管理费用+财务费用+研发费用), 得出结果为{date}年{company_name}的企业研发经费占费用比例是{stat_dict[key]}"
                
            elif key == '三费比重':
                template = f"{company_name}在{date}年的销售费用为{stat_dict['销售费用']}元，管理费用为{stat_dict['管理费用']}元，财务费用为{stat_dict['财务费用']}元，营业收入为{stat_dict['营业收入']}元，根据公式，三费比重 = ( 销售费用 + 管理费用 + 财务费用) / 营业收入, 得出结果为{company_name}在{date}年的三费比重是{stat_dict[key]}"
            
            elif key == '硕士及以上人员占职工人数比例':
                template = f"{company_name}在{date}年的硕士人数是{stat_dict['硕士人数']}人，博士及以上人数是{stat_dict['博士及以上']}人，职工总数是{stat_dict['职工总数']}，根据公式，企业硕士及以上人员占职工人数比例 = ( 硕士人数 + 博士及以上人数) / 职工总数。得出结果为{company_name}在{date}年的企业硕士及以上人员占职工人数比例{stat_dict[key]}"
                
            elif key == '比例':
                pass
            
            else:
                key1, key2 = ratio_key_dict[key]
                template = f"{company_name}在{date}年的{key1}为{stat_dict[key1]}元，在{date}年的{key2}为{stat_dict[key2]}元，根据公式{key}={key1}/{key2}，得出{company_name}在{date}的{key}是{stat_dict[key]}"
                
        # finacial keys
        elif sample['category'] == 3:
            date = int(date[0])
            if '和' in key and key != '联营企业和合营企业投资收益':
                key1, key2 = key.split('和')[0], key.split('和')[1]
                template = f"{company_name}在{date}年的{key1}是{stat_dict[key1]}元，{key2}是{stat_dict[key2]}元"
            else:
                template = f"{company_name}在{date}年的{key}是{stat_dict[key]}元"
        
        elif sample['category'] == 4:
            pass

        elif stat_dict == None:
            # 无法回答的问题
            template = f'*****'
        
        sample['prompt'] = template
        
