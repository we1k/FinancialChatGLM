#! /bin/bash

gpu_num=$(echo $CUDA_VISIBLE_DEVICES | awk -F ',' '{print NF}')
echo $gpu_num $CUDA_VISIBLE_DEVICES

#1. 将所有pdf文件转化为txt储存
python dev/pdf2txt.py

#2. 对问题进行正则匹配，获取对应keyword
python dev/extract_question.py

#3. 解析每个lines_txt中对应的txt文件，获取三大基本表 + 公司信息 + 员工信息
python dev/extract_report.py

#4.查询每个问题对应的数据表，添加到额外的问题字段`prompt`
python dev/search.py

#5. 使用chatglm进行推断
bash scripts/local_eval.sh

#6. post-progress处理
python dev/post_process.py