FROM python:3-alpine

RUN pip install pipenv
RUN apt-get update
RUN apt-get install iputils
RUN pip install configparser
RUN pip install influxdb
WORKDIR /app

COPY isp-outage-tracker.conf.example .

COPY . .

CMD [ "python3", "-u", "main.py" ]