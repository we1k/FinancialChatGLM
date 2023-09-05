# ChatGLM金融大模型挑战赛: 随便起个名

## Repo structure:

/data/finQA_smp: 存储年报pdf文件

/dev: 存储数据预处理代码

/src && /scripts: 存储ChatGLM2 Finetune及Inference代码

## Quick Start
1. 将所有pdf文件转化为txt储存
```
python dev/pdf2txt.py
```
此时获取data/lines_txt所有处理好的txt文件

2. 对问题进行正则匹配，获取对应keyword
```
python dev/extract_question.py
```

获取data/questions/test.json，其中每一个record包含了对应的`Company_name`，`DATE`，`task_key`
1. 解析每个lines_txt中对应的txt文件，获取三大基本表 + 公司信息 + 员工信息
```
python dev/extract_report.py
```
此时获取data/tables中以``<公司__年份>``储存的对应解析文件，以csv格式存储。(避免sql查询)

1. 查询每个问题对应的数据表，添加到额外的问题字段`prompt`
```
python dev/search.py
```
此时将处理好的数据集放在`data/smp2023/dataset.json`

1. 使用chatglm2模型进行推断
```
bash scripts/eval.sh
```
获得最终输出结果在`output`文件夹中

## Miscellaneous
