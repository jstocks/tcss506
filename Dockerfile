FROM python:slim-buster
RUN pip install flask
COPY app.py /usr/local/bin/app.py
COPY static /usr/local/bin/static
COPY templates /usr/local/bin/templates
CMD /usr/local/bin/app.py
