FROM python:3.10

WORKDIR /warehouse_app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY models models
COPY schemas schemas
COPY database.py .
COPY main.py .
