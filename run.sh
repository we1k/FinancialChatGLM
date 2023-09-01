#! /bin/bash

#1. 将所有pdf文件转化为txt储存
# 直接可以从alltxt中读取

echo "Good Luck!!"

#2. 建立数据库
python dev/create_table.py

#3. 建立对应pdf的向量缩影
python dev/embeddings.py

#4. 对问题进行正则匹配，获取对应keyword
python dev/extract_question.py

#5. 解析每个lines_txt中对应的txt文件，获取三大基本表 + 公司信息 + 员工信息
python dev/extract_report.py
# python dev/transfer_file.py

#6.查询每个问题对应的数据表，添加到额外的问题字段`prompt`
python dev/search.py

#7. 使用chatglm进行推断
bash scripts/eval.sh

#8. post-progress处理
python dev/post_process.py
