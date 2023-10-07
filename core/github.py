import logging

import requests
from django.core.cache import cache

logger = logging.getLogger("django")


class GitHubException(Exception):
    pass


class RateLimitedException(GitHubException):
    pass


class GitHub:
    BASE_URL = "https://api.github.com/repos/random-rip/primebot_backend"
    RELEASES = BASE_URL + "/releases"
    RELEASES_CACHE_KEY = "releases"
    CACHE_DURATION = 60 * 60

    @classmethod
    def get_json(cls, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 403:
            raise RateLimitedException(f"Github Rate limit: {response.json()}")
        else:
            raise GitHubException(
                f"GitHub API returned status code {response.status_code}. Content: f{response.json()}"
            )

    @classmethod
    def releases(cls):
        cached = cache.get(cls.RELEASES_CACHE_KEY)
        if cached:
            logger.debug("Using cached releases")
            return cached
        try:
            logger.debug("Fetching releases")
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            return data
        except Exception as e:
            logger.error("Error fetching releases: " + str(e))
            return []

    @classmethod
    def latest_version(cls) -> dict:
        cached = cache.get(cls.RELEASES_CACHE_KEY)
        ret = {
            "version": None,
            "released_at": None,
            "body": None,
        }
        if cached:
            logger.debug("Using cached latest release")
            ret["version"] = cached[0].get("tag_name", None)
            ret["released_at"] = cached[0].get("published_at", None)
            ret["body"] = cached[0].get("body", None)
            return ret
        try:
            logger.debug("Fetching latest release")
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            ret["version"] = data[0].get("tag_name", None)
            ret["released_at"] = data[0].get("published_at", None)
            ret["body"] = data[0].get("body", None)
            return ret
        except Exception as e:
            logger.error(e)
            return ret
