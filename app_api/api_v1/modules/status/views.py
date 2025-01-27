import logging
import subprocess

from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from app_prime_league.models import ChannelTeam, Team
from core.api import PrimeLeagueAPI
from core.github import GitHub

logger = logging.getLogger("django")


@extend_schema(exclude=True)
class ChangelogView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        github_data = GitHub.releases()
        changelogs = [
            {"version": x["tag_name"], "released_at": x["published_at"], "notes": x["body"]} for x in github_data
        ]
        data = {
            "changelogs": changelogs,
        }
        return Response(data)


@extend_schema(exclude=True)
class StatusView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        logger.info("Request PrimeBot Website")
        data = {
            "latest": GitHub.latest_version().to_dict(),
            "prime_league_status": self._get_prime_league_status(),
            "discord_status": self._get_discord_bot_status(),
            "telegram_status": self._get_telegram_bot_status(),
            "registered_teams": Team.objects.get_registered_teams().count(),
            "subscribed_teams": ChannelTeam.objects.count(),
            "total_teams": Team.objects.all().count(),
        }
        return Response(data)

    def _get_prime_league_status(self):
        cache_key = "prime_league_status"
        cache_duration = 60
        cached = cache.get(cache_key)
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
        cached = cache.get(cache_key)
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
        cached = cache.get(cache_key)
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
