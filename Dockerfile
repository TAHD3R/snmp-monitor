FROM python:3.11
LABEL version="0.1.0"
LABEL description="Tempreature and Humidity monitor script for BUCT"
LABEL org.opencontainers.image.authors="jaasaar@126.com"

ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE=false

RUN mkdir -p /app
WORKDIR /app

RUN echo "deb http://mirrors.aliyun.com/debian/ buster main non-free contrib" > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security/ buster/updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian-security/ buster/updates main non-free contrib" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y libsnmp-dev snmp-mibs-downloader

RUN mkdir ~/.pip && \
    echo "[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/\ntrusted-host = mirrors.aliyun.com" > ~/.pip/pip.conf
RUN pip install poetry -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./ /app/
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root

CMD ["python", "main.py"]