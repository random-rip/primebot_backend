#!/bin/sh
cd /root/prime_league_bot && nohup venv/bin/python manage.py runscript run_bot > logs/run_bot.log 2>&1 &
echo $! > logs/run_bot_pid.txt