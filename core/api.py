import niquests
from django.conf import settings

from utils.exceptions import PrimeLeagueConnectionException


class PrimeLeagueAPI:
    _TEAM = "/team/%s/"
    _MATCH = "/match/%s/"
    BASE_URL = settings.GAME_SPORTS_BASE_URL

    @classmethod
    def request(cls, endpoint, request_method=niquests.get, query_params=None, **kwargs):
        """
        :param endpoint:
        :param request_method:
        :param query_params: optional list of strings
        :param kwargs: optional params passed to niquests method
        :return:
        :raises: PrimeLeagueConnectionException
        """
        if endpoint is None:
            raise Exception("Endpoint cannot be None")
        path = f"{cls.BASE_URL}{endpoint}"
        if query_params:
            path += "?"
            path += "&".join(str(x) for x in [query_params])

        default_requests_params = {
            "timeout": 10,
        }
        try:
            response = request_method(url=path, **{**default_requests_params, **kwargs})
        except niquests.exceptions.ConnectionError:
            raise PrimeLeagueConnectionException()
        return response

    @classmethod
    def request_match(cls, match_id):
        return cls.request(cls._MATCH % match_id)

    @classmethod
    def request_team(cls, team_id, **kwargs):
        """

        Args:
            team_id:
            **kwargs: optional params passed to requests method

        Returns:

        """
        return cls.request(cls._TEAM % team_id, **kwargs)
