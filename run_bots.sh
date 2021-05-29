#!/bin/sh
/root/prime_league_bot/venv/bin/python manage.py runscript run_discord_bot &
/root/prime_league_bot/venv/bin/python manage.py runscript run_telegram_bot &
