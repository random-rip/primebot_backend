import logging
from typing import Callable

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
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


def enqueue_messages(message_template):
    teams = Team.objects.get_registered_teams()
    for team in teams:
        try:
            collector = MessageCollector(team)
            collector.dispatch(msg_class=VersionUpdateMessage, custom_message=message_template)
        except Exception as e:
            logger = logging.getLogger("notifications")
            logger.exception(e)


class EnqueueMessagesJob(Job):
    """
    Enqueues a version update message to all registered teams.
    """

    __name__ = 'EnqueueMessage'

    def function_to_execute(self) -> Callable:
        return enqueue_messages

    def __init__(self, message_template):
        self.message_template = message_template

    def kwargs(self) -> dict:
        return {
            "message_template": self.message_template,
        }
