FROM python:3.10.12 as base

# where your code lives
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install lsb-release -y
RUN apt-get -y install apt-utils

# MariaDB
RUN apt-get -y install libmariadb-dev libssl-dev

RUN pip install --upgrade pip

# copy whole project to your docker home directory.
COPY requirements.txt requirements.prod.txt ./
# run this command to install all dependencies
RUN pip install -r requirements.prod.txt

COPY . .

RUN apt-get install gettext -y

RUN python manage.py compilemessages -l de --settings=primebot_backend.static # temp

FROM base as static_files

RUN python manage.py collectstatic --no-input --settings=primebot_backend.static # temp

FROM caddy as fileserver

COPY --from=static_files /var/www/primebot.me/static/ /www/html
