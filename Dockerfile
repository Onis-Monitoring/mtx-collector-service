# FROM python:3.6.5-slim
FROM python:2.7-slim

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

ENV PYTHONUNBUFFERED=0

COPY . /app

EXPOSE 5000

# ENTRYPOINT [ "python" ]

CMD ["python", "-u", "app.py"]
