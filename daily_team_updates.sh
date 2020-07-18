#!/bin/sh
cd /root/prime_league_bot && venv/bin/python manage.py runscript team_updates >> logs/daily_team_updates.log &
