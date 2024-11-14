"""
Django settings for primebot_backend project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import errno
import os
from datetime import datetime
from pathlib import Path

import environ
import pytz
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env.str('DJANGO_SECRET_KEY', default="")
FERNET_KEY = env.str("FERNET_SECRET_KEY", default="")

DEBUG = env.bool('DJANGO_DEBUG', default=False)
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", cast=str, default=[])

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", cast=str, default=[])

INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS = [
    "admin_interface",
    'quicklinks_admin',
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
    "request_queue",
    "request",
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'request.middleware.RequestMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

ROOT_URLCONF = 'primebot_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'quicklinks_admin/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

X_FRAME_OPTIONS = "SAMEORIGIN"
SILENCED_SYSTEM_CHECKS = ["security.W019"]

WSGI_APPLICATION = 'primebot_backend.wsgi.application'

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB"),
        "USER": env.str("POSTGRES_USER"),
        "PASSWORD": env.str("POSTGRES_PASSWORD"),
        "HOST": env.str("POSTGRES_HOST"),
        "PORT": env.str("POSTGRES_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en'

LANGUAGES = (
    ("de", _("German")),
    ("en", _("English")),
)

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True


USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env.str("STATIC_ROOT", None)

MEDIA_URL = '/media/'
MEDIA_ROOT = env.str("MEDIA_ROOT", None)

GAME_SPORTS_BASE_URL = env.str("GAME_SPORTS_BASE_URL", None)

PRM_BASE_URI = "https://www.primeleague.gg/de/leagues/"
MATCH_URI = PRM_BASE_URI + "matches/"
TEAM_URI = PRM_BASE_URI + "teams/"
SPLIT_URI = "splits/"

SITE_ID = env.str("SITE_ID", None)

CURRENT_SPLIT_START = datetime(2024, 1, 29).astimezone(pytz.timezone("Europe/Berlin"))

STORAGE_DIR = os.path.join(BASE_DIR, "storage")

TELEGRAM_BOT_KEY = env.str("TELEGRAM_BOT_API_KEY", None)
TG_DEVELOPER_GROUP = env.int("TG_DEVELOPER_GROUP", None)
TELEGRAM_START_LINK = "https://t.me/prime_league_bot?startgroup=start"

DISCORD_BOT_KEY = env.str("DISCORD_API_KEY", None)
DISCORD_APP_CLIENT_ID = env.int("DISCORD_APP_CLIENT_ID", None)
DISCORD_SERVER_LINK = "https://discord.gg/K8bYxJMDzu"
DISCORD_GUILD_ID = env.int("DISCORD_GUILD_ID", None)  # Only used for development

IMAGE_STATIC_DIR = BASE_DIR / "bots" / "static"
LOGIN_URL = "/.admin/login/"

GITHUB_URL = "https://github.com/random-rip/primebot_backend"
GITHUB_API_TOKEN = env.str("GITHUB_API_TOKEN", None)

LOGGING_DIR = env.str("LOGGING_DIR", "logs")
try:
    os.mkdir(LOGGING_DIR)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise exc
    pass

DEFAULT_SCOUTING_NAME = "op.gg"
DEFAULT_SCOUTING_URL = "https://www.op.gg/multisearch/euw?summoners={}"
DEFAULT_SCOUTING_SEP = ","

TEMP_LINK_TIMEOUT_MINUTES = 60

FILES_FROM_STORAGE = env.bool("FILES_FROM_STORAGE", False)

CACHES = {
    'default': (
        {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
        if DEBUG
        else {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': env.str('CACHE_LOCATION', "redis://redis:6379"),
        }
    )
}

LOCALE_PATHS = [
    BASE_DIR / "bots" / "locale",
    BASE_DIR / "app_prime_league" / "locale",
]

MONGODB_URI = env.str("MONGODB_URI", None)
if MONGODB_URI is None:
    MONGODB_URI = (
        f"mongodb://{env.str('MONGODB_USERNAME', '')}:{env.str('MONGODB_PASSWORD', 'localhost')}"
        f"@{env.str('MONGODB_HOST', '')}:{env.str('MONGODB_PORT', 27017)}"
    )

__MAXIMUM_TIMEOUT = 60 * 13  # 14,5 minutes for the updater
Q_CLUSTER = {
    'timeout': __MAXIMUM_TIMEOUT,
    'retry': __MAXIMUM_TIMEOUT + 60,  # Seconds after a failed task will be queued again
    'max_attempts': 1,  # Maximum attempts for tasks
    'save_limit': 10_000,  # Limits the amount of successful tasks save to Django
    "ack_failures": False,
    "workers": 1,
    "catch_up": False,
    "log_level": "DEBUG",
    "recycle": 10,
    "sync": env.bool("MONGODB_SYNC", DEBUG),
    "orm": "default",
    # 'mongo': {
    #     'host': MONGODB_URI,
    #     "serverSelectionTimeoutMS": 5_000,
    #     "connect": False,
    # },
    "time_zone": "Europe/Berlin",
    "ALT_CLUSTERS": {
        "messages": {
            "timeout": 20,  # 20 seconds
            "retry": 30,  # 30 seconds
            "max_attempts": 3,
            "workers": 4,
            "log_level": "DEBUG",
            "recycle": 10,
        },
    },
}

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'teams': '1000/day',
        'matches': '1000/day',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    "PAGE_SIZE": 100,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
}

# OPEN API SPECTACULAR

SPECTACULAR_SETTINGS = {
    'TITLE': 'PrimeBot API',
    'DESCRIPTION': 'Provides information about teams, players and matches of the Techniker Prime League.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}

# Django Request
REQUEST_LOG_IP = True
REQUEST_LOG_USER = False
REQUEST_IGNORE_PATHS = (
    r"^.admin/",
    r"^favicon.ico",
)
REQUEST_TRAFFIC_MODULES = (
    "request.traffic.UniqueVisitor",
    "request.traffic.Hit",
    "request.traffic.Ajax",
    "request.traffic.Error",
)
if not DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'to_file': {
                'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
                'datefmt': "%d/%b/%Y %H:%M:%S",
            },
            'to_console': {'format': '[%(levelname)s] %(name)s: %(message)s'},
        },
        'handlers': {
            'console': {
                'level': "DEBUG",
                'formatter': 'to_console',
                'class': 'logging.StreamHandler',
            },
            # "portainer": {
            #     'level': "INFO",
            #     'formatter': 'to_console',
            #     'class': 'logging.StreamHandler',
            # },
            'django': {
                'level': "INFO",
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': os.path.join(LOGGING_DIR, 'django.log'),
                'formatter': 'to_file',
            },
            'notifications': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': os.path.join(LOGGING_DIR, 'notifications.log'),
                'formatter': 'to_file',
            },
            'commands': {
                'level': 'INFO',
                'class': 'logging.handlers.WatchedFileHandler',
                'filename': os.path.join(LOGGING_DIR, 'commands.log'),
                'formatter': 'to_file',
            },
            'updates': {
                'level': "INFO",
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOGGING_DIR, 'updates.log'),
                'when': 'midnight',
                'formatter': 'to_file',
            },
            'discord': {
                'level': "INFO",
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOGGING_DIR, 'discord.log'),
                'when': 'midnight',
                'formatter': 'to_file',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['django', 'console'],
                'level': "WARNING",
                'propagate': False,
            },
            'notifications': {
                'handlers': ['notifications', 'console'],
                'level': "INFO",
                'propagate': False,
            },
            'commands': {
                'handlers': [
                    'commands',
                    'console',
                ],
                'level': "INFO",
                'propagate': False,
            },
            'updates': {
                'handlers': ['updates'],
                'level': "INFO",
                'propagate': False,
            },
            'discord': {
                'handlers': ['discord'],
                'level': "INFO",
                'propagate': False,
            },
        },
    }
