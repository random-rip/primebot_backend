import os
import time

import numpy as np
import requests

from prime_league_bot import settings
from utils.exceptions import PrimeLeagueConnectionException, TeamWebsite404Exception


def get_local_response(file_name, file_path=None):
    file_path = os.path.join(settings.STORAGE_DIR if file_path is None else file_path, file_name)
    with open(file_path, 'r', encoding='utf8') as f:
        text = f.read()
    return text


def save_object_to_file(obj, file_name):
    file_path = os.path.join(settings.STORAGE_DIR, file_name)
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(obj)


user_agent_list = (
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/94.0.4606.52 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/94.0.4606.52 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPod; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/94.0.4606.52 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A205U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A102U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-N960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-Q720) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-X420) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; LM-Q710(FGN)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Mobile Safari/537.36",
    # ===
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.6; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (X11; Linux i686; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/37.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 11_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/37.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (iPod touch; CPU iPhone OS 11_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) FxiOS/37.0 Mobile/15E148 Safari/605.1.15",
    "Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/92.0",
    "Mozilla/5.0 (Android 11; Mobile; LG-M255; rv:92.0) Gecko/92.0 Firefox/92.0",
    # ===
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPod touch; CPU iPhone 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
)


class Api:
    def __init__(self):
        self.base_uri = settings.LEAGUES_URI
        self.base_uri_ajax = settings.AJAX_URI
        self.apply_blacklist_robustness = not settings.DEBUG

    def _get_html_headers(self):
        return {
            'user-agent': self._get_random_user_agent(),
            'referer': 'https://www.primeleague.gg/',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': "1",
            'sec-ch-ua': 'Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
            "sec-ch-ua-mobile": '?0',
            "sec-ch-ua-platform": 'Windows',
            "sec-fetch-dest": 'document',
            "sec-fetch-mode": 'navigate',
            "sec-fetch-site": 'same-origin',
            "sec-fetch-user": '?1',
        }

    def delay(self, min_milliseconds=100, max_milliseconds=4000, constant_milliseconds=None):
        if not self.apply_blacklist_robustness:
            return
        if constant_milliseconds is not None:
            assert isinstance(constant_milliseconds, int), "constant_milliseconds is no integer!"
            time.sleep(constant_milliseconds / 1000)
        else:
            time.sleep(np.random.randint(min_milliseconds, max_milliseconds) / 1000)

    def _get_json_headers(self):
        return {
            'user-agent': self._get_random_user_agent(),
            'referer': 'https://www.primeleague.gg/',
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': ' max-age=0',
            'x-requested-with': 'XMLHttpRequest',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        }

    def _get_random_user_agent(self):
        return user_agent_list[np.random.randint(0, len(user_agent_list))]

    def json_handler(self, endpoint, request=requests.post, post_params=None, ):
        if endpoint is None:
            raise Exception("Endpoint not found")

        path = f"{self.base_uri_ajax}{endpoint}/"
        self.delay()
        response = request(url=path, data=post_params, headers=self._get_html_headers())
        return response

    def html_handler(self, endpoint, request=requests.get, query_params=None, ):
        """
        :param endpoint:
        :param request:
        :param query_params:
        :return:
        :raises: PrimeLeagueConnectionException
        """
        if endpoint is None:
            raise Exception("Endpoint not found")
        path = f"{self.base_uri}{endpoint}"
        path += "/".join(str(x) for x in [query_params]) if query_params is not None else ""

        self.delay()
        try:
            response = request(path, headers=self._get_html_headers())
        except requests.exceptions.ConnectionError:
            raise PrimeLeagueConnectionException()
        return response


class Crawler:

    def __init__(self, local: bool = False):
        """

        :param local: If local is True, the crawler is using text documents from storage folder.
        """
        self.local = local
        self.api = Api()
        self.save_requests = settings.DEBUG and not local
        if self.save_requests:
            print("Consider using the local file system in development to reduce the number of requests.")

    def get_match_website(self, match_id):
        if self.local:
            return get_local_response(f"match_{match_id}.txt")
        resp = self.api.html_handler(f"matches/{match_id}", )
        if resp.status_code == 404:
            return None
        if resp.status_code == 429:
            raise Exception("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            save_object_to_file(resp.text, f"match_{match_id}.txt")
        return resp.text

    def get_team_website(self, _id):
        """

        :param _id:
        :return:
        :raises, TeamWebsite404Exception, PrimeLeagueConnectionException,
        """
        if self.local:
            text = get_local_response(f"team_{_id}.txt")
            return text
        resp = self.api.html_handler(f"teams/{_id}")
        if resp.status_code == 404:
            raise TeamWebsite404Exception()
        if resp.status_code == 429:
            raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            save_object_to_file(resp.text, f"team_{_id}.txt")
        return resp.text

    def get_match_details_json(self, match):
        if self.local:
            return get_local_response(f"match_details_json_{match}.txt")
        resp = self.api.json_handler(f"leagues_match", post_params={"id": match, "action": "init", "language": "de"})
        if resp.status_code == 404:
            raise TeamWebsite404Exception()
        if resp.status_code == 429:
            raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            save_object_to_file(resp.text, f"match_details_json_{match}.txt")
        return resp.text

    def get_comments_json(self, match):
        if self.local:
            return get_local_response(f"comments_json_{match}.txt")
        resp = self.api.json_handler(f"comments_load", post_params={
            "init": 1,
            "m": "league_match",
            "language": "de",
            "i": match
        })
        if resp.status_code == 404:
            raise TeamWebsite404Exception()
        if resp.status_code == 429:
            raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            save_object_to_file(resp.text, f"comments_json_{match}.txt")
        return resp.text


crawler = Crawler(local=False)
