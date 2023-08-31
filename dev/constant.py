import os
import sys

RATIO_KEY = ['流动比率', '速动比率', '现金比率', '资产负债比率',  '毛利率', '净利润率', '流动负债比率', '非流动负债比率',
    '三费比重', '财务费用率', '管理费用率',
    '营业成本率', '营业利润率', 
    '现金及现金等价物增长率', '流动负债增长率',
    '总资产增长率', '总负债增长率', '货币资金增长率',
    '净利润增长率', '投资收益增长率',
    '管理费用增长率', '财务费用增长率', 
    '研发费用增长率', '销售费用增长率', 
    '无形资产增长率', '固定资产增长率', 
    '营业利润增长率', '营业收入增长率', 
    '投资收益占营业收入比率', '研发经费与营业收入比值', 
    '研发经费占费用比例',
    '研发经费与利润比值', 
    '研发人员占职工人数比例', '硕士及以上人员占职工人数比例'
]
RATIO_KEY.sort(key=lambda x:-len(x))

BASIC_KEY = [
    '电子信箱', '企业名称', '办公地址', '注册地址', '外文名称', '证券简称',
    '法定代表人', '证券代码', '公司网址', '法定代表人是否相同',
    '职工总数', '技术人员数', '博士及以上', '硕士人数', '研发人员数', '销售人员数',
    '实际控制人', '控股股东是否发生变更',
]
BASIC_KEY.sort(key=lambda x:-len(x))

FINANCIAL_KEY = [
    # financial
     ## 财务报表
    # 合并资产负债表
    '负债合计', '应付职工薪酬', '资产总计', '非流动资产合计', '流动资产合计', 
    '应收款项融资', '货币资金',
    '衍生金融资产和其他非流动金融资产', '衍生金融资产', '其他非流动金融资产',
    '固定资产和无形资产', '固定资产', '无形资产', '存货', '股本',
    '交易性金融资产', '应收账款', '预付款项', '应付账款', 
    '流动资产', '非流动资产', '其他流动资产', '其他非流动资产', 
    '短期借款和长期借款', '短期借款', '长期借款',
    '在建工程', '资本公积',
    '盈余公积', '未分配利润', '递延所得税负债', 
    '流动负债', '非流动负债', '应收票据', '应付票据',
    '应交税费', '所有者权益合计', 
    '负债和所有者权益', '商誉',
    '长期应收款', '长期股权投资', '租赁负债',
    '资本支出', '资产减值损失', '债权投资',

    # 合并利润表 
    '营业利润', '营业成本', '营业收入', '营业成本和营业利润', 
    '营业外支出', '营业外收入', '销售收入',
    '营业收入和营业外收入',
    '利息支出和利息收入', '利息支出', '利息收入',
    '营业外支出和营业外收入',  '投资收益', '变动收益',
    '研发费用和财务费用', '研发费用', '财务费用', 
    '销售费用和管理费用', '销售费用', '管理费用', 
    '利润总额和净利润', '利润总额', '净利润', 
    '所得税费用', '综合收益总额', '税金及附加', 
    '联营企业和合营企业投资收益',
    '投资收益', '利息收入', '投资收益', '公允价值变动收益',
    '信用减值损失', '资产减值损失', '资产处置收益', 
    '持续经营净利润', '营业总收入', '营业总成本',
    '营业外收支净额', '归属于母公司所有者权益合计',

    # 合并现金流量表
    '收回投资收到现金', '现金及现金等价物余额', 
    '投资支付', '经营活动现金流入', '经营活动现金流出',
    '投资活动现金流入', '投资活动现金流出', '筹资活动现金流出',
    '筹资活动现金流入', '现金及现金等价物净增加额',
    # 总股本/总股数
    ### unrecog #找出总股数，计算得到  净资产 / 普通股总数, '营业总成本'
    '每股收益和每股净资产', '每股收益', '每股净资产', '每股经营现金流量',
]
FINANCIAL_KEY.sort(key=lambda x:-len(x))

ANALYSIS_KEY = [
    # analysis
    '报告期内公司环境信息', '主要销售客户集中度', '供应商情况', '控股股东及实控人', '董事、监事、高级管理人员报酬', '研发投入情况', '审计意见情况', '聘任、解聘会计师事务情况', '主要供应商情况', '重大关联交易情况', '社会责任工作情况', '营业收入构成整体情况', '现金流量净额变动原因' , '非标准审计报告', '资产及负债状况',
    '营业收入变动情况及原因', '投资收益变动原因', "控股股东、实控人诚信状况",
    '简要介绍', '简要概述', 
    '分析', '情况', '原因', 
]
ANALYSIS_KEY.sort(key=lambda x:-len(x))


VAGUE_MAPPING = {
    '法定代表人是否相同' : ['法定代表人相比相同吗', '法定代表人是否都相同', '法定代表人是否有都是相同'],
    '硕士人数': ['硕士员工人数', '硕士研究生员工数量'],
    '电子信箱': ['电子邮箱'],
    '实际控制人': ['实控人是谁'],
    '简要概述': ['简述', '概述'],
    '公司网址': ['网站'],
    '职工总数': ['总职工', '员工总数', '职工总人数'],
    '外文名称': ['英文名称'],
    '技术人员数': ['技术员工人数', '技术人员人数'],
    '销售人员数': ['销售员工人数', '销售人员人数'],
    '研发人员数': ['研发员工人数', '研发人员人数'],
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
    '收回投资收到现金' : ['收回投资现金', '收回投资所收到现金', '收回投资所得到现金'],
    '股本' : ['实收资本', '实收资本(或股本)']
}


KEY_REMAPPING = {
    "研发经费与利润比值" : "企业研发经费与利润比值",
    "研发经费与营业收入比值" : "企业研发经费与营业收入比值",
    "硕士及以上人员占职工人数比例" : "企业硕士及以上人员占职工人数比例",
    "研发经费占费用比例" : "企业研发经费占费用比例",
    "联营企业和合营企业投资收益" : "联营企业和合营企业的投资收益",
    "收回投资收到现金" : "收回投资收到的现金",
    "现金及现金等价物余额"  : "期末现金及现金等价物余额",
    "流动负债" : "流动负债合计",
    "非流动负债" : "非流动负债合计",
    "流动资产" : "流动资产合计",
    "非流动资产" : "非流动资产合计",
}


DEBT_KEY = ['负债合计', '应付职工薪酬', '资产总计', 
            '非流动资产合计', '流动资产合计', '应收款项融资', '货币资金', 
            '衍生金融资产', '其他非流动金融资产',
            '固定资产', '无形资产', '存货', '股本',
            '交易性金融资产', '应收账款', '预付款项', '应付账款', 
            '其他流动资产', '其他非流动资产', '短期借款', '长期借款', '在建工程', '资本公积',
            '盈余公积', '未分配利润', '递延所得税负债', 
            '流动负债', '非流动负债', '应收票据', '应付票据',
            '应交税费', '所有者权益合计', '归属于母公司所有者权益合计',
            '负债和所有者权益',
            ]

PROFIT_KEY = ['营业利润', '营业成本', '营业收入',
            '营业外支出', '营业外收入',
            '利息支出', '利息收入',
            '投资收益', '变动收益',
            '研发费用', '财务费用', 
            '销售费用', '管理费用', 
            '利润总额', '净利润', 
            '所得税费用', '综合收益总额', '税金及附加', 
            '联营企业和合营企业投资收益',
            '公允价值变动收益',
            '信用减值损失', '资产减值损失', '资产处置收益',
            '持续经营净利润', '营业总收入', '营业总成本',
            ]

CASH_KEY = ['收回投资收到现金', '现金及现金等价物余额', 
            '投资支付', '经营活动现金流入', '经营活动现金流出',
            '投资活动现金流入', '投资活动现金流出', '筹资活动现金流出',
            '筹资活动现金流入', '现金及现金等价物净增加额',
            ]