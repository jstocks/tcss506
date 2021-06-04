FROM python:slim-buster
WORKDIR /usr/src/flask_project
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN apt-get update && apt-get -y install git wget
RUN pip3 install -r requirements.txt
RUN wget -c https://github.com/flask-extensions/Flask-GoogleMaps/archive/refs/tags/0.4.1.1.tar.gz -O - | tar -xz
RUN cd Flask-GoogleMaps-* && pip3 install .
COPY . .