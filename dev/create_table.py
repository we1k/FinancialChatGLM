import sqlite3
import os
import re
import json
import csv

from constant import DEBT_KEY, PROFIT_KEY, CASH_KEY, KEY_REMAPPING

path = './data/tables/'

def create_debt(foldername):
    try:
        empty_debt = [0] * (3 + len(DEBT_KEY))
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
                    for i in range(len(DEBT_KEY)):
                        minlength = 99
                        for item in table:
                            if DEBT_KEY[i] in item[0]:
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
        empty_profit = [0] * (3 + len(PROFIT_KEY))
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
                    for i in range(len(PROFIT_KEY)):
                        minlength = 99
                        for item in table:
                            if PROFIT_KEY[i] in item[0] or (KEY_REMAPPING.get(PROFIT_KEY[i], "None") in item[0]):
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
        empty_cash = [0] * (3 + len(CASH_KEY))
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
                    for i in range(len(CASH_KEY)):
                        minlength = 99
                        for item in table:
                            if CASH_KEY[i] in item[0] or (KEY_REMAPPING.get(CASH_KEY[i], "None") in item[0]):
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
    key_list = [f"{key} DECIMAL(20, 2)" for key in DEBT_KEY]
    create_command = ",\n".join(key_list)
    create_command = f'''CREATE TABLE IF NOT EXISTS debt
                (公司名称 VARCHAR(10),
                年份 INT,
                注册地址 TEXT,
                {create_command},
                PRIMARY KEY (公司名称, 年份))
                '''
    cursor.execute(create_command)
    
    key_list = [f"{key} DECIMAL(20, 2)" for key in PROFIT_KEY]
    create_command = ",\n".join(key_list)
    create_command = f'''CREATE TABLE IF NOT EXISTS profit
                (公司名称 VARCHAR(10),
                年份 INT,
                注册地址 TEXT,
                {create_command},
                PRIMARY KEY (公司名称, 年份))
                '''
    cursor.execute(create_command)

    key_list = [f"{key} DECIMAL(20, 2)" for key in CASH_KEY]
    create_command = ",\n".join(key_list)
    create_command = f'''CREATE TABLE IF NOT EXISTS cash
                (公司名称 VARCHAR(10),
                年份 INT,
                注册地址 TEXT,
                {create_command},
                PRIMARY KEY (公司名称, 年份))
                '''
    cursor.execute(create_command)
    
    # for foldername in os.listdir(path):
    #     command = create_profit(foldername)

    with open('./tcdata/B-list-pdf-name.txt','r',encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            parts = line.split('__')
            foldername = parts[3] + '__' + parts[4]
            #print(parts[3] + '__' + parts[4])
            command = create_debt(foldername)
            print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            command = create_profit(foldername)
            print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            command = create_cash(foldername)
            #print(command)
            if len(command) > 0:
                cursor.execute(command)
            
            conn.commit()
    # test on db
    cursor.execute("SELECT 公司名称, 年份, 注册地址 FROM debt")
    rows = cursor.fetchall()
    # for row in rows:
        # print(row)


if __name__ == "__main__":
    create_db()