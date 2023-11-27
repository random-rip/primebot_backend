import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = "not_really_secret"
DEBUG = False
TELEGRAM_BOT_KEY = None
STATIC_ROOT = "/var/www/primebot.me/static/"
STATIC_URL = "/static/"
INSTALLED_APPS = [
    "admin_interface",
    "colorfield",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 3rd party
    "rest_framework",
    'django_extensions',
    "corsheaders",
    "django_q",
    'drf_spectacular',
    "debug_toolbar",
    'django_filters',
    # own
    'app_prime_league',
    'core',
    'bots',
]
