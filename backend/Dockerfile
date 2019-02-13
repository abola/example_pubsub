FROM python:slim-stretch

RUN mkdir -p /python
COPY requirements.txt /python/requirements.txt
RUN pip install -r /python/requirements.txt

ADD app /python/app

RUN mkdir -p /etc/google/auth
COPY pubsub.json /etc/google/auth/pubsub.json

EXPOSE 80

CMD ["/usr/local/bin/python3", "/python/process.py"]