import requests

from prime_league_bot import settings
from utils.exceptions import PrimeLeagueConnectionException


class PrimeLeagueConnector:
    _TEAM = "/team/%s/"
    _MATCH = "/match/%s/"

    def __init__(self):
        self.base_url = settings.GAME_SPORTS_BASE_URL

    def _get_json_headers(self):
        return {
            # 'referer': 'https://www.primeleague.gg/',
            # 'accept': '*/*',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            # 'cache-control': ' max-age=0',
            # 'x-requested-with': 'XMLHttpRequest',
            # 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

    def json_handler(self, endpoint, request=requests.get, query_params=None, ):
        """
        :param endpoint:
        :param request:
        :param query_params:
        :return:
        :raises: PrimeLeagueConnectionException
        """
        if endpoint is None:
            raise Exception("Endpoint cannot be None")
        path = f"{self.base_url}{endpoint}/"
        if query_params:
            path += "?"
            path += "&".join(str(x) for x in [query_params])

        try:
            response = request(url=path, headers=self._get_json_headers())
        except requests.exceptions.ConnectionError:
            raise PrimeLeagueConnectionException()
        return response.json()

    def match(self, match_id):
        return self.json_handler(self._MATCH % match_id)

    def team(self, team_id):
        return self.json_handler(self._TEAM % team_id)
