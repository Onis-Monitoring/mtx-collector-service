# FROM python:3.6.5-slim
FROM python:2.7-slim

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
COPY ./print_event_repository_loader_trace.py /app/print_event_repository_loader_trace.py

WORKDIR /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app

EXPOSE 5000

# ENTRYPOINT [ "python" ]

CMD ["python", "-u", "app.py"]