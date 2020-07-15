#!/bin/sh
cd /root/prime_league_bot && nohup venv/bin/python manage.py runscript run_bot > my.log 2>&1 &
echo $! > run_bot_pid.txt