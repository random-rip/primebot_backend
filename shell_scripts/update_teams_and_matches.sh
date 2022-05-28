#!/bin/sh
cd /opt/prime_bot/prime_bot_backend/ && venv/bin/python manage.py update_teams && venv/bin/python manage.py update_matches &
