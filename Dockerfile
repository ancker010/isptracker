FROM python:3-alpine

RUN pip install pipenv
RUN apk update
RUN apk add iputils
RUN pip install configparser
RUN pip install influxdb
WORKDIR /app

COPY isp-outage-tracker.conf.example .

COPY . .

CMD [ "python3", "-u", "main.py" ]