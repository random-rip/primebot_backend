#!/bin/sh
cd /root/prime_league_bot && venv/bin/python manage.py runscript main >> logs/main.log &
