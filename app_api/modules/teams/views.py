import logging
import subprocess

import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from app_prime_league.models import Team
from core.api import PrimeLeagueAPI

logger = logging.getLogger("django")
