import os

from modules.connector import PrimeLeagueConnector
from prime_league_bot import settings
from utils.exceptions import TeamWebsite404Exception, PrimeLeagueConnectionException


class PrimeLeagueProvider:
    """
    Providing JSON Responses from api or file system.
    If settings.FILES_FROM_STORAGE is True, the crawler is using text documents from storage folder.
    """
    __TEAM_FILE_PATTERN = "team_%s.json"
    __MATCH_FILE_PATTERN = "match_%s.json"

    def __init__(self):
        self.local = settings.FILES_FROM_STORAGE
        self.api = PrimeLeagueConnector()
        self.save_requests = settings.DEBUG and not self.local
        if self.save_requests:
            print("Consider using the local file system in development to reduce the number of requests.")

    def get_match(self, match_id):
        file_name = f"match_{match_id}.json"
        if self.local:
            return self.__get_local_response(file_name)
        resp = self.api.match(match_id)
        if resp.status_code == 404:
            return None
        if resp.status_code == 429:
            raise Exception("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            self.__save_object_to_file(resp.text, file_name)
        return resp.text

    def get_team(self, team_id):
        """

        :param team_id:
        :return:
        :raises, TeamWebsite404Exception, PrimeLeagueConnectionException,
        """
        if self.local:
            text = self.__get_local_team_response(team_id)
            return text
        resp = self.api.team(team_id)
        if resp.status_code == 404:
            raise TeamWebsite404Exception()
        if resp.status_code == 429:
            raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
        if self.save_requests:
            self.__save_team_to_file(resp.text, team_id)
        return resp.text

    @classmethod
    def __get_local_team_response(cls, team_id):
        return cls.__get_local_response(cls.__TEAM_FILE_PATTERN % team_id)

    @classmethod
    def __get_local_match_response(cls, match_id):
        return cls.__get_local_response(cls.__MATCH_FILE_PATTERN % match_id)

    @classmethod
    def __save_team_to_file(cls, obj, team_id):
        return cls.__save_object_to_file(obj, cls.__TEAM_FILE_PATTERN % team_id)

    @classmethod
    def __save_match_to_file(cls, obj, match_id):
        return cls.__save_object_to_file(obj, cls.__MATCH_FILE_PATTERN % match_id)

    @classmethod
    def __get_local_response(cls, file_name, file_path=None):
        file_path = os.path.join(settings.STORAGE_DIR if file_path is None else file_path, file_name)
        with open(file_path, 'r', encoding='utf8') as f:
            text = f.read()
        return text

    @classmethod
    def __save_object_to_file(cls, obj, file_name):
        file_path = os.path.join(settings.STORAGE_DIR, file_name)
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(obj)
