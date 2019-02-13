FROM python:slim-stretch

RUN apt-get update && apt-get install -y supervisor

RUN mkdir -p /python
COPY requirements.txt /python/requirements.txt
RUN pip install -r /python/requirements.txt

ADD app /python/app
COPY supervisord.conf /python/supervisord.conf

RUN mkdir -p /etc/google/auth
COPY pubsub.json /etc/google/auth/pubsub.json

EXPOSE 80

ENTRYPOINT ["/usr/bin/supervisord", "-c", "/python/supervisord.conf"]