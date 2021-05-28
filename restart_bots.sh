#!/bin/sh
pkill -9 -f "venv/bin/python manage.py runscript run"
wait
cd /root/prime_league_bot && venv/bin/python manage.py runscript run_discord_bot >> logs/discord.log & venv/bin/python manage.py runscript run_telegram_bot &
