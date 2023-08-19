FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-devel

COPY . /app
WORKDIR /app
RUN ls
# RUN pip install --no-cache-dir -r requirements.txt --index-url=http://mirrors.aliyun.com/pypi/simple/ --trusted-host=mirrors.aliyun.com


CMD ["bash", "run.sh"]