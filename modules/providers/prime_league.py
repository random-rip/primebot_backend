import json
import os

from modules.api import PrimeLeagueAPI
from prime_league_bot import settings
from utils.exceptions import TeamWebsite404Exception, PrimeLeagueConnectionException, PrimeLeagueParseException

LOCAL = settings.FILES_FROM_STORAGE
SAVE_REQUEST = settings.DEBUG and not LOCAL
if SAVE_REQUEST:
    print("Consider using the local file system in development to reduce the number of requests.")


class PrimeLeagueProvider:
    """
    Providing JSON Responses from api or file system.
    If settings.FILES_FROM_STORAGE is True, the crawler is using text documents from storage folder.
    """
    __TEAM_FILE_PATTERN = "team_%s.json"
    __MATCH_FILE_PATTERN = "match_%s.json"
    api = PrimeLeagueAPI

    @classmethod
    def get_match(cls, match_id):
        """
        Args:
            match_id:

        Returns:
        Exceptions: PrimeLeagueConnectionException, PrimeLeagueParseException
        """
        file_name = f"match_{match_id}.json"
        if LOCAL:
            return cls.__get_local_json(file_name)
        resp = cls.api.request_match(match_id)
        if resp.status_code == 404:
            return None
        if resp.status_code == 429:
            raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
        if SAVE_REQUEST:
            cls.__save_object_to_file(resp.text, file_name)
        try:
            return resp.json()
        except ValueError:
            raise PrimeLeagueParseException()

    @classmethod
    def get_team(cls, team_id):
        """

        Args:
            team_id:
        Returns: Team JSON
        Exceptions: TeamWebsite404Exception, PrimeLeagueConnectionException, PrimeLeagueParseException
        """
        if LOCAL:
            text_json = cls.__get_local_team_response(team_id)
        else:
            resp = cls.api.request_team(team_id)
            try:
                text_json = resp.json()
                team_id = text_json.get("team").get("team_id")
                if team_id is None:
                    raise TeamWebsite404Exception
            except (ValueError, KeyError):
                raise PrimeLeagueParseException()
            if resp.status_code == 404:
                raise TeamWebsite404Exception()
            if resp.status_code == 429:
                raise PrimeLeagueConnectionException("Error Statuscode 429: Too many Requests")
            if SAVE_REQUEST:
                cls.__save_team_to_file(resp.text, team_id)
        return text_json

    @classmethod
    def __get_local_team_response(cls, team_id):
        return cls.__get_local_json(cls.__TEAM_FILE_PATTERN % team_id)

    @classmethod
    def __get_local_match_response(cls, match_id):
        return cls.__get_local_json(cls.__MATCH_FILE_PATTERN % match_id)

    @classmethod
    def __save_team_to_file(cls, obj, team_id):
        return cls.__save_object_to_file(obj, cls.__TEAM_FILE_PATTERN % team_id)

    @classmethod
    def __save_match_to_file(cls, obj, match_id):
        return cls.__save_object_to_file(obj, cls.__MATCH_FILE_PATTERN % match_id)

    @classmethod
    def __get_local_json(cls, file_name, file_path=None):
        file_path = os.path.join(settings.STORAGE_DIR if file_path is None else file_path, file_name)
        with open(file_path, 'r', encoding='utf8') as f:
            text = f.read()
        return json.loads(text)

    @classmethod
    def __save_object_to_file(cls, obj, file_name):
        file_path = os.path.join(settings.STORAGE_DIR, file_name)
        with open(file_path, 'w+', encoding='utf8') as f:
            f.write(obj)
