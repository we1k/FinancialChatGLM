import sqlite3
import os
import re
import json
import csv

debtkey = ['公司名称', '年份', '注册地址', '负债合计', '应付职工薪酬', '资产总计', '非流动资产合计', '应收款项融资', '货币资金', 
            '衍生金融资产', '其他非流动金融资产',
            '固定资产', '无形资产', '存货', '股本',
            '交易性金融资产', '应收账款', '预付款项', '应付账款', 
            '其他非流动资产', '短期借款', '在建工程', '资本公积',
            '盈余公积', '未分配利润', '递延所得税负债']

profitkey = ['公司名称', '年份', '注册地址', '营业利润', '营业成本', '营业收入',
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
            '持续经营净利润', '营业总收入', '营业总成本']

cashkey = ['公司名称', '年份', '注册地址', '收回投资收到现金', '现金及现金等价物余额', 
            '投资支付', '经营活动现金流入', '经营活动现金流出',
            '投资活动现金流入', '投资活动现金流出', '筹资活动现金流出',
            '筹资活动现金流入', '现金及现金等价物净增加额']

keymapping = {
    "联营企业和合营企业投资收益" : "联营企业和合营企业的投资收益",
    "收回投资收到现金" : "收回投资收到的现金",
    "现金及现金等价物余额"  : "期末现金及现金等价物余额"
}

path = './data/tables/'

def create_debt(foldername):
    try:
        empty_debt = [0] * 26
        for filename in os.listdir(path+foldername):
            if re.match("基本信息表.json", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    json_data = json.load(fd)
                    empty_debt[0] = json_data['文档公司名']
                    empty_debt[1] = int(json_data['年份'].strip('年'))
                    empty_debt[2] = json_data['注册地址']
            if re.match(".*合并资产负债表.*\.csv", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    sheet = csv.reader(fd)
                    header = next(sheet)
                    table = []
                    index1 = -1
                    index2 = -1
                    for index,it in enumerate(header):
                        if re.match('项目', it.replace(' ','')):
                            index1 = index
                        if re.match('%d年12月31日'%(empty_debt[1]), it.replace(' ','')):
                            index2 = index
                    if index1 == -1 or index2 == -1:
                        continue
                    for row in sheet:
                        table.append([row[index1], row[index2]])
                    for i in range(3, 26):
                        minlength = 99
                        for item in table:
                            if debtkey[i] in item[0]:
                                if len(item[0]) < minlength:
                                    if re.match("-+[^0-9]", item[1]+" ") or "－" in item[1] or '不适用' in item[1] or '/' in item[1]:
                                        empty_debt[i] = 0
                                    else:
                                        empty_debt[i] = float(item[1].replace(' ','').replace(',','').strip('(').strip(')'))
                                    minlength = len(item[0])
        #print('INSERT INTO debt VALUES (%s)'%(str(empty_debt).strip('[').strip(']')))
        # break
        #cursor.execute('INSERT INTO debt VALUES (%s)'%(str(empty_debt).strip('[').strip(']')))
        #conn.commit()
        return 'INSERT INTO debt VALUES (%s)'%(str(empty_debt).strip('[').strip(']'))
    except ValueError as err:
        print(foldername)
        print(err)
        return ''

def create_profit(foldername):
    try:
        empty_profit = [0] * 29
        for filename in os.listdir(path+foldername):
            if re.match("基本信息表.json", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    json_data = json.load(fd)
                    empty_profit[0] = json_data['文档公司名']
                    empty_profit[1] = int(json_data['年份'].strip('年'))
                    empty_profit[2] = json_data['注册地址']
            if re.match(".*合并利润表.*\.csv", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    sheet = csv.reader(fd)
                    header = next(sheet)
                    table = []
                    index1 = -1
                    index2 = -1
                    for index,it in enumerate(header):
                        if re.match('项目', it.replace(' ','')):
                            index1 = index
                        if re.match('%d年度'%(empty_profit[1]), it.replace(' ','')):
                            index2 = index
                    if index1 == -1 or index2 == -1:
                        continue
                    for row in sheet:
                        table.append([row[index1], row[index2]])
                    for i in range(3, 29):
                        minlength = 99
                        for item in table:
                            if profitkey[i] in item[0] or (i == 21 and keymapping[profitkey[i]] in item[0]):
                                if len(item[0]) < minlength:
                                    if re.match("-+[^0-9]", item[1]+" ") or "－" in item[1] or '不适用' in item[1] or '/' in item[1]:
                                        empty_profit[i] = 0
                                    else:
                                        empty_profit[i] = float(item[1].replace(' ','').replace(',','').strip('(').strip(')'))
                                    minlength = len(item[0])
        return 'INSERT INTO profit VALUES (%s)'%(str(empty_profit).strip('[').strip(']'))
    except ValueError as err:
        print(foldername)
        print(err)
        return ''

def create_cash(foldername):
    try:
        empty_cash = [0] * 13
        for filename in os.listdir(path+foldername):
            if re.match("基本信息表.json", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    json_data = json.load(fd)
                    empty_cash[0] = json_data['文档公司名']
                    empty_cash[1] = int(json_data['年份'].strip('年'))
                    empty_cash[2] = json_data['注册地址']
            if re.match(".*合并现金流量表.*\.csv", filename):
                with open(os.path.join(path+foldername, filename), 'r',encoding='utf-8') as fd:
                    sheet = csv.reader(fd)
                    header = next(sheet)
                    table = []
                    index1 = -1
                    index2 = -1
                    for index,it in enumerate(header):
                        if re.match('项目', it.replace(' ','')):
                            index1 = index
                        if re.match('%d年度'%(empty_cash[1]), it.replace(' ','')):
                            index2 = index
                    if index1 == -1 or index2 == -1:
                        continue
                    for row in sheet:
                        table.append([row[index1], row[index2]])
                    for i in range(3, 13):
                        minlength = 99
                        for item in table:
                            if cashkey[i] in item[0] or ((i == 3 or i == 4) and keymapping[cashkey[i]] in item[0]):
                                if len(item[0]) < minlength:
                                    if re.match("-+[^0-9]", item[1]+" ") or "－" in item[1] or '不适用' in item[1] or '/' in item[1]:
                                        empty_cash[i] = 0
                                    else:
                                        empty_cash[i] = float(item[1].replace(' ','').replace(',','').strip('(').strip(')'))
                                    minlength = len(item[0])
        return 'INSERT INTO cash VALUES (%s)'%(str(empty_cash).strip('[').strip(']'))
    except ValueError as err:
        print(foldername)
        print(err)
        return ''

def create_db():
    if os.path.exists('company.db'):
        os.remove('company.db')
    conn = sqlite3.connect('company.db')

    # 创建游标对象
    cursor = conn.cursor()

    # 创建表
    cursor.execute('''CREATE TABLE IF NOT EXISTS debt
                    (公司名称 VARCHAR(10),
                    年份 INT,
                    注册地址 TEXT,
                    负债合计 DECIMAL(20, 2),
                    应付职工薪酬 DECIMAL(20, 2),
                    资产总计 DECIMAL(20, 2),
                    非流动资产合计 DECIMAL(20, 2),
                    应收款项融资 DECIMAL(20, 2),
                    货币资金 DECIMAL(20, 2),
                    衍生金融资产 DECIMAL(20, 2),
                    其他非流动金融资产 DECIMAL(20, 2),
                    固定资产 DECIMAL(20, 2),
                    无形资产 DECIMAL(20, 2),
                    存货 DECIMAL(20, 2),
                    股本 DECIMAL(20, 2),
                    交易性金融资产 DECIMAL(20, 2),
                    应收账款 DECIMAL(20, 2),
                    预付款项 DECIMAL(20, 2),
                    应付账款 DECIMAL(20, 2),
                    其他非流动资产 DECIMAL(20, 2),
                    短期借款 DECIMAL(20, 2),
                    在建工程 DECIMAL(20, 2),
                    资本公积 DECIMAL(20, 2),
                    盈余公积 DECIMAL(20, 2),
                    未分配利润 DECIMAL(20, 2),
                    递延所得税负债 DECIMAL(20, 2),
                    PRIMARY KEY (公司名称, 年份))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS profit
                    (公司名称 VARCHAR(10),
                    年份 INT,
                    注册地址 TEXT,
                    营业利润 DECIMAL(20, 2),
                    营业成本 DECIMAL(20, 2),
                    营业收入 DECIMAL(20, 2),
                    营业外支出 DECIMAL(20, 2),
                    营业外收入 DECIMAL(20, 2),
                    利息支出 DECIMAL(20, 2),
                    利息收入 DECIMAL(20, 2),
                    投资收益 DECIMAL(20, 2),
                    变动收益 DECIMAL(20, 2),
                    研发费用 DECIMAL(20, 2),
                    财务费用 DECIMAL(20, 2),
                    销售费用 DECIMAL(20, 2),
                    管理费用 DECIMAL(20, 2),
                    利润总额 DECIMAL(20, 2),
                    净利润 DECIMAL(20, 2),
                    所得税费用 DECIMAL(20, 2),
                    综合收益总额 DECIMAL(20, 2),
                    税金及附加 DECIMAL(20, 2),
                    联营企业和合营企业投资收益 DECIMAL(20, 2),
                    公允价值变动收益 DECIMAL(20, 2),
                    信用减值损失 DECIMAL(20, 2),
                    资产减值损失 DECIMAL(20, 2),
                    资产处置收益 DECIMAL(20, 2),
                    持续经营净利润 DECIMAL(20, 2),
                    营业总收入 DECIMAL(20, 2),
                    营业总成本 DECIMAL(20, 2),
                    PRIMARY KEY (公司名称, 年份))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cash
                (公司名称 VARCHAR(10),
                年份 INT,
                注册地址 TEXT,
                收回投资收到现金 DECIMAL(20, 2),
                现金及现金等价物余额 DECIMAL(20, 2),
                投资支付 DECIMAL(20, 2),
                经营活动现金流入 DECIMAL(20, 2),
                经营活动现金流出 DECIMAL(20, 2),
                投资活动现金流入 DECIMAL(20, 2),
                投资活动现金流出 DECIMAL(20, 2),
                筹资活动现金流出 DECIMAL(20, 2),
                筹资活动现金流入 DECIMAL(20, 2),
                现金及现金等价物净增加额 DECIMAL(20, 2),
                PRIMARY KEY (公司名称, 年份))''')
    
    # for foldername in os.listdir(path):
    #     command = create_profit(foldername)

    with open('./tcdata/B-list-pdf-name.txt','r',encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.split('__')
            foldername = parts[3] + '__' + parts[4]
            #print(parts[3] + '__' + parts[4])
            command = create_debt(foldername)
            #print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            command = create_profit(foldername)
            #print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            command = create_cash(foldername)
            #print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            conn.commit()
    # test on db
    # cursor.execute("SELECT 公司名称, 年份, 货币资金 FROM debt ORDER BY 货币资金 DESC LIMIT 10")
    # rows = cursor.fetchall()
    # for row in rows:
    #     print(row)


if __name__ == "__main__":
    create_db()