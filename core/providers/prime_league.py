import json
import os

from django.conf import settings
from rest_framework import status

from core.api import PrimeLeagueAPI
from utils.exceptions import (
    TeamWebsite404Exception, PrimeLeagueConnectionException, PrimeLeagueParseException,
    Match404Exception, UnauthorizedException)

LOCAL = settings.FILES_FROM_STORAGE
SAVE_REQUEST = settings.DEBUG and not LOCAL
if SAVE_REQUEST:
    print("Consider using the local file system in development to reduce the number of requests.")
if LOCAL:
    print(
        "\tYou are currently serving files over the local storage. Cool!"
        "\t(To change this behaviour set FILES_FROM_STORAGE='False' in your .env)"
    )


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
        Exceptions: PrimeLeagueConnectionException, PrimeLeagueParseException, Match404Exception
        """
        file_name = f"match_{match_id}.json"
        if LOCAL:
            return cls.__get_local_json(file_name)

        resp = cls.api.request_match(match_id)

        if not status.is_success(resp.status_code):
            if resp.status_code == status.HTTP_404_NOT_FOUND:
                raise Match404Exception(status_code=resp.status_code, msg=f"Match {match_id}")
            if resp.status_code == status.HTTP_403_FORBIDDEN and settings.DEBUG:
                raise UnauthorizedException()
            raise PrimeLeagueConnectionException(status_code=resp.status_code, msg=f"Match {match_id}")

        if SAVE_REQUEST:
            cls.__save_object_to_file(resp.text, file_name)

        try:
            return resp.json()
        except ValueError:
            raise PrimeLeagueParseException(msg=f"Match {match_id}")

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
            return text_json

        resp = cls.api.request_team(team_id)
        if not status.is_success(resp.status_code):
            if resp.status_code == status.HTTP_404_NOT_FOUND:
                raise TeamWebsite404Exception(msg=f"Team {team_id}")
            if resp.status_code == status.HTTP_403_FORBIDDEN and settings.DEBUG:
                raise UnauthorizedException()
            raise PrimeLeagueConnectionException(status_code=resp.status_code, msg=f"Team {team_id}")

        try:
            text_json = resp.json()
            team_id = text_json.get("team").get("team_id")
            if team_id is None:
                raise TeamWebsite404Exception(msg=f"Team {team_id}")
        except (ValueError, KeyError, json.decoder.JSONDecodeError):
            raise PrimeLeagueParseException(msg=f"Team {team_id}")

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
        try:
            with open(file_path, 'r', encoding='utf8') as f:
                text = f.read()
        except FileNotFoundError:
            raise TeamWebsite404Exception(msg=f"This team was not found on filesystem.")
        return json.loads(text)

    @classmethod
    def __save_object_to_file(cls, obj, file_name):
        file_path = os.path.join(settings.STORAGE_DIR, file_name)
        with open(file_path, 'w+', encoding='utf8') as f:
            f.write(obj)
