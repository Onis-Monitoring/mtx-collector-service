# FROM python:3.6.5-slim
# FROM python:2.7-slim
FROM mtx-engine
LABEL maintainer="Edgar Lopez"
LABEL version="2.0"
USER root
RUN yum install -y gcc python-devel net-snmp-devel
RUN pip install --upgrade "pip < 21.0"
RUN pip install --upgrade setuptools
# RUN yum install -y kubectl
# We copy just the requirements.txt first to leverage Docker cache

COPY ./requirements.txt /home/mtx/gunicorn/app/requirements.txt

# COPY ./print_event_repository_loader_trace.py /app/print_event_repository_loader_trace.py

WORKDIR /home/mtx/gunicorn

# RUN apt-get update && apt-get install -y iputils-ping iputils-tracepath

# RUN apt-get update && apt-get install -y gcc libc-dev python2-dev net-snmp net-snmp-dev

RUN pip install --trusted-host pypi.python.org -r ./app/requirements.txt

# USER mtx

ENV PYTHONUNBUFFERED=0

COPY . /home/mtx/gunicorn



EXPOSE 5000

CMD ["gunicorn", "-w", "3", "-b", ":5000", "app.main:create_app()", "--timeout", "90"]
# CMD ["gunicorn", "-w", "1", "-b", ":5000", "app.test:create_app()", "--timeout", "90"]