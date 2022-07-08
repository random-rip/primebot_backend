import logging
import subprocess

import requests
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from app_prime_league.models import Team
from core.api import PrimeLeagueAPI

logger = logging.getLogger("django")


class GitHub:
    BASE_URL = "https://api.github.com/repos/random-rip/primebot_backend"
    RELEASES = BASE_URL + "/releases"
    RELEASES_CACHE_KEY = "releases"
    CACHE_DURATION = 60 * 60

    @classmethod
    def get_json(cls, url):
        data = requests.get(url).json()
        return data

    @classmethod
    def releases(cls):

        cached = cache.get(cls.RELEASES_CACHE_KEY, )
        if cached:
            return cached
        try:
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            return data
        except Exception:
            return []

    @classmethod
    def latest_version(cls) -> dict:
        cached = cache.get(cls.RELEASES_CACHE_KEY, )
        ret = {
            "version": None,
            "released_at": None,
        }
        if cached:
            ret["version"] = cached[0].get("tag_name", None)
            ret["released_at"] = cached[0].get("published_at", None)
            return ret
        try:
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            ret["version"] = data[0].get("tag_name", None)
            ret["released_at"] = data[0].get("published_at", None)
            return ret
        except Exception:
            return ret


class ChangelogView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        github_data = GitHub.releases()
        changelogs = [
            {
                "version": x["tag_name"],
                "released_at": x["published_at"],
                "notes": x["body"]
            }
            for x in github_data
        ]
        data = {
            "changelogs": changelogs,
        }
        return Response(data)


class StatusView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        logger.info("Request PrimeBot Website")
        data = {
            "latest": GitHub.latest_version(),
            "prime_league_status": self._get_prime_league_status(),
            "discord_status": self._get_discord_bot_status(),
            "telegram_status": self._get_telegram_bot_status(),
            "registered_teams": Team.objects.get_registered_teams().count(),
            "total_teams": Team.objects.all().count(),
        }
        return Response(data)

    def _get_prime_league_status(self):
        cache_key = "prime_league_status"
        cache_duration = 60
        cached = cache.get(cache_key, )
        if cached:
            return cached
        try:
            response = PrimeLeagueAPI.request_team(1, timeout=5)
            data = response.status_code == 200
            cache.set(cache_key, data, cache_duration)
            return data
        except Exception:
            return False

    def _get_discord_bot_status(self):
        cache_key = "discord_bot_status"
        cache_duration = 60
        cached = cache.get(cache_key, )
        if cached:
            return cached
        try:
            stat = subprocess.call(["systemctl", "is-active", "--quiet", "discord_bot"])
            is_active = stat == 0
            cache.set(cache_key, is_active, cache_duration)
            return is_active
        except FileNotFoundError:
            return None
        except Exception:
            return False

    def _get_telegram_bot_status(self):
        cache_key = "telegram_bot_status"
        cache_duration = 60
        cached = cache.get(cache_key, )
        if cached:
            return cached
        try:
            stat = subprocess.call(["systemctl", "is-active", "--quiet", "telegram_bot"])
            is_active = stat == 0
            cache.set(cache_key, is_active, cache_duration)
            return is_active
        except FileNotFoundError:
            return None
        except Exception:
            return False
