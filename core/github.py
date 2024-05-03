import logging
from dataclasses import dataclass
from typing import Union

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("django")


class GitHubException(Exception):
    pass


class RateLimitedException(GitHubException):
    pass


@dataclass
class GitHubData:
    version: str = None
    released_at: str = None
    body: str = None

    def to_dict(self):
        return {
            "version": self.version,
            "released_at": self.released_at,
            "body": self.body,
        }


class GitHub:
    BASE_URL = "https://api.github.com/repos/random-rip/primebot_backend"
    RELEASES = BASE_URL + "/releases"
    RELEASES_CACHE_KEY = "github_releases"
    CACHE_DURATION = 60 * 60

    @classmethod
    def get_json(cls, url: str) -> Union[dict, list]:
        headers = {}
        if settings.GITHUB_API_TOKEN is not None:
            headers["Authorization"] = "token " + settings.GITHUB_API_TOKEN
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 403:
            raise RateLimitedException(f"Github Rate limit: {response.json()}")
        if response.status_code == 429:
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
    def latest_version(cls) -> GitHubData:
        all_releases: list = cache.get(cls.RELEASES_CACHE_KEY)
        latest_release = None
        if all_releases is None:
            logger.warning("Fetching latest releases")
            all_releases = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, all_releases, cls.CACHE_DURATION)
            if len(all_releases) > 0:
                latest_release = all_releases[0]
        if all_releases is not None and len(all_releases) > 0:
            latest_release = all_releases[0]
        if latest_release is None:
            return GitHubData()
        else:
            return GitHubData(
                version=latest_release["tag_name"],
                released_at=latest_release["published_at"],
                body=latest_release["body"],
            )
