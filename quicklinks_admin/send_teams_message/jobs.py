import logging
from typing import Callable

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCreatorJob
from bots.messages import NotificationToTeamMessage
from core.cluster_job import Job
from core.github import GitHub


class VersionUpdateMessage(NotificationToTeamMessage):
    template = """Hallo {team.name},

🔥 Version {github.version} ist draußen 🔥

{github.body}

Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/information/changelog

Sternige Grüße
– PrimeBot devs
"""

    def __init__(self, team: Team, custom_message=None, **message_elements):
        super().__init__(
            team=team,
            custom_message=custom_message or self.template,
            github=GitHub.latest_version(),
            **message_elements,
        )


def enqueue_messages(message_template: str, team_ids: list[int] = None):
    """
    Enqueues a version update message to all registered teams or a subset of registered teams.
    Recursively enqueues the message for failed teams.
    """
    teams = Team.objects.get_registered_teams()
    if team_ids:
        teams = teams.filter(id__in=team_ids)
    failed_team_ids = []
    for team in teams:
        try:
            collector = MessageCreatorJob(
                msg_class=VersionUpdateMessage,
                team=team,
                custom_message=message_template,
            )
            collector.enqueue()
        except Exception as e:
            failed_team_ids.append(team.id)
            logger = logging.getLogger("notifications")
            logger.exception(e)
    if failed_team_ids:
        EnqueueMessagesJob(message_template=message_template, team_ids=failed_team_ids).enqueue()


class EnqueueMessagesJob(Job):
    """
    Enqueues a version update message to all registered teams.
    """

    __name__ = 'EnqueueMessage'

    def function_to_execute(self) -> Callable:
        return enqueue_messages

    def __init__(self, message_template, team_ids: list[int] = None):
        self.message_template = message_template
        self.team_ids = team_ids

    def get_kwargs(self) -> dict:
        return {
            "message_template": self.message_template,
            "team_ids": self.team_ids,
        }
