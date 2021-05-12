FROM python:slim-buster
WORKDIR /usr/src/flask_project
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
COPY . .
