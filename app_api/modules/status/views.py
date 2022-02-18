import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView


class StatusView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, ):
        gitlab_data = self._latest_release()
        data = {
            "version": gitlab_data.get("tag_name"),
            "latest_changes": gitlab_data.get("description"),
            "prime_league_status": self._get_prime_league_status(),
            "discord_status": self._get_discord_bot_status(),
            "telegram_status": self._get_telegram_bot_status()
        }
        return Response(data)

    def _latest_release(self):
        cache_key = "latest_release"
        cache_duration = 60 * 60
        cached = cache.get(cache_key, )
        if cached:
            return cached
        try:
            data = requests.get("https://gitlab.com/api/v4/projects/19644883/releases/",
                                headers={"PRIVATE-TOKEN": settings.GIT_TOKEN}).json()[0]

            cache.set(cache_key, data, cache_duration)
            return data
        except Exception:
            return {}

    def _get_prime_league_status(self):
        cache_key = "prime_league_status"
        cache_duration = 60 * 15
        cached = cache.get(cache_key, )
        if cached:
            return cached
        try:
            response = requests.get(f"{settings.TEAM_URI}1", )
            data = response.status_code == 200
            cache.set(cache_key, data, cache_duration)
            return data
        except Exception:
            return False

    def _get_discord_bot_status(self):
        try:
            return
        except Exception:
            return False

    def _get_telegram_bot_status(self):
        try:
            return
        except Exception:
            return False
