# FROM python:3.6.5-slim
FROM python:2.7-slim
LABEL maintainer="Edgar Lopez"
LABEL version="2.0"

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
# COPY ./print_event_repository_loader_trace.py /app/print_event_repository_loader_trace.py

WORKDIR /app

RUN apt-get update && apt-get install -y iputils-ping iputils-tracepath

# RUN apt-get update && apt-get install -y gcc libc-dev python2-dev net-snmp net-snmp-dev

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENV PYTHONUNBUFFERED=0

COPY . /app

EXPOSE 5000

CMD ["gunicorn", "-w", "3", "-b", ":5000", "app.main:create_app()", "--timeout", "90"]