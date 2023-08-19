# FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel
# FROM registry.cn-shanghai.aliyuncs.com/tcc-public/pytorch:2.0.0-py3.9.12-cuda11.8.0-u22.04
FROM registry.cn-shanghai.aliyuncs.com/tcc-public/pytorch:1.12-py3.9.12-cuda11.3.1-u20.04

RUN apt-get update && apt-get install -y curl zip && apt-get clean

COPY . /app
WORKDIR /app
RUN ls
RUN pip install --no-cache-dir -r requirements.txt --index-url=http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com


CMD ["bash", "run.sh"]