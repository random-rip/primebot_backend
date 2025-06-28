FROM python:3.10 as base
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

# where your code lives
WORKDIR /app
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install lsb-release -y
RUN apt-get -y install apt-utils

COPY . .

RUN apt-get install gettext -y

RUN uv run manage.py compilemessages -l de --settings=primebot_backend.static # temp

FROM base as static_files

RUN uv run manage.py collectstatic --no-input --settings=primebot_backend.static # temp

FROM caddy as fileserver

COPY --from=static_files /var/www/primebot.me/static/ /www/html
