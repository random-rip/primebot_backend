from datetime import datetime, timedelta
from time import sleep

from rest_framework import status

from core.providers.base import Provider
from request_queue import EndpointType, RequestQueue, push
from utils.exceptions import (
    Match404Exception,
    PrimeLeagueConnectionException,
    TeamWebsite404Exception,
    UnauthorizedException,
)


class RequestQueueProvider(Provider):
    """
    Providing JSON Responses from api or file system.
    If settings.FILES_FROM_STORAGE is True, the crawler is using text documents from storage folder.
    """

    def __init__(self, priority, force=False):
        self.priority = priority
        self.force = force

    def get_match(self, match_id) -> dict:
        """
        :param match_id: the id of the match
        :return: match data as a dictionary
        :raise PrimeLeagueConnectionException:
        :raise PrimeLeagueParseException:
        :raise Match404Exception:
        """
        response = self._get_or_wait(EndpointType.MATCH, match_id)

        if response is None:
            raise PrimeLeagueConnectionException(msg=f"Match {match_id}: Job disappeared, WTF?")

        if status.is_success(response["status_code"]):
            return response["payload"]
        else:
            if response["status_code"] == status.HTTP_404_NOT_FOUND:
                raise Match404Exception(status_code=response["status_code"], msg=f"Match {match_id}")
            elif response["status_code"] == status.HTTP_403_FORBIDDEN:
                raise UnauthorizedException()
            raise PrimeLeagueConnectionException(status_code=response["status_code"], msg=f"Match {match_id}")

    def get_team(self, team_id) -> dict[str, str]:
        """
        :param team_id: the id of the team
        :return: team data as a dictionary
        :raise PrimeLeagueConnectionException:
        :raise PrimeLeagueParseException:
        :raise TeamWebsite404Exception:
        """
        response = self._get_or_wait(EndpointType.TEAM, team_id)
        if response is None:
            raise PrimeLeagueConnectionException(msg=f"Team {team_id}: Job disappeared, WTF?")

        if status.is_success(response["status_code"]):
            return response["payload"]
        else:
            if response["status_code"] == status.HTTP_404_NOT_FOUND:
                raise TeamWebsite404Exception(msg=f"Team {team_id}")
            elif response["status_code"] == status.HTTP_403_FORBIDDEN:
                raise UnauthorizedException()
            raise PrimeLeagueConnectionException(status_code=response["status_code"], msg=f"Team {team_id}")

    def _get_or_wait(self, endpoint: EndpointType, detail_id: int) -> dict[str, str | dict | datetime] | None:
        """
        Get the latest response from responses if the entry's
        - last_crawled timestamp is less than 15 minutes,
        - entry is not None,
        - status_code is 200 and
        - force is False
        or pushes the job and wait until it's done.
        :param endpoint: Endpoint that should be used
        :param detail_id: teamID or matchID
        :return:
        """
        queue = RequestQueue()
        if not self.force:
            latest_response = queue.get_response(endpoint, detail_id)
            if (
                latest_response is not None
                and status.is_success(latest_response["status_code"])
                and latest_response["last_crawled"] > datetime.utcnow() + timedelta(minutes=15)
            ):
                return latest_response
        job_id = push(endpoint, detail_id, priority=self.priority)

        while queue.job_is_queued(job_id):
            sleep(1)

        response = queue.get_response(endpoint, detail_id)
        return response
