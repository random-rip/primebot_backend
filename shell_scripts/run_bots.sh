#!/bin/sh
echo $PATH
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
/root/prime_league_bot/venv/bin/python manage.py runscript run_discord_bot &
/root/prime_league_bot/venv/bin/python manage.py runscript run_telegram_bot &
