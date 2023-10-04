FROM python:3.10.12 as base

# where your code lives
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED=0

RUN apt-get update
RUN apt-get install lsb-release -y
RUN apt-get -y install apt-utils

# MariaDB
RUN apt-get -y install libmariadb-dev libssl-dev

RUN pip install --upgrade pip

# copy whole project to your docker home directory.
COPY requirements.txt requirements.txt
# run this command to install all dependencies
RUN pip install -r requirements.txt

FROM base as app

WORKDIR /app

COPY . .

CMD python manage.py migrate

EXPOSE 8000

CMD python manage.py runserver app:8000
