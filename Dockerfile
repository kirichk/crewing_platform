# Dockerfile
FROM python:3.7.6
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
RUN pip install urllib3==1.23
ADD crewing /code/
