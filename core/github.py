import logging

import requests
from django.core.cache import cache


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
        cached = cache.get(cls.RELEASES_CACHE_KEY)
        if cached:
            logging.getLogger("django").warning("Using cached releases")
            return cached
        try:
            logging.getLogger("django").warning("Fetching releases")
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            return data
        except Exception:
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
            logging.getLogger("django").warning("Using cached latest release")
            ret["version"] = cached[0].get("tag_name", None)
            ret["released_at"] = cached[0].get("published_at", None)
            ret["body"] = cached[0].get("body", None)
            return ret
        try:
            logging.getLogger("django").warning("Fetching latest release")
            data = cls.get_json(cls.RELEASES)
            cache.set(cls.RELEASES_CACHE_KEY, data, cls.CACHE_DURATION)
            ret["version"] = data[0].get("tag_name", None)
            ret["released_at"] = data[0].get("published_at", None)
            ret["body"] = data[0].get("body", None)
            return ret
        except Exception:
            return ret
