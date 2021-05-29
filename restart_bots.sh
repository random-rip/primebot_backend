#!/bin/sh
pkill -15 -f "venv/bin/python manage.py runscript run"
wait
cd /root/prime_league_bot/ || exit
wait
venv/bin/python manage.py runscript run_discord_bot &
venv/bin/python manage.py runscript run_telegram_bot &
