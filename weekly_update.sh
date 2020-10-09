#!/bin/sh
cd /root/prime_league_bot && venv/bin/python manage.py runscript weekly_notification >> logs/weekly_update.log &
