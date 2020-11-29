# Dockerfile
FROM python:3.7.6
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
ADD crewing /code/
