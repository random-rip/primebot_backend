from typing import Any, Callable, Dict, Type

from app_prime_league.models import Team
from bots.messages.base import BaseMessage
from core.cluster_job import Job

from .dispatcher import MessageDispatcherJob


def create_and_dispatch_message(msg_class: Type[BaseMessage], team: Team, **kwargs):
    """
    Creates a message and enqueues a `MessageDispatcherJob` for each subscribed channel
    """
    assert issubclass(msg_class, BaseMessage)
    for channel_team in team.channel_teams.all():
        msg = msg_class(channel_team=channel_team, **kwargs)
        if not msg.team_wants_notification():
            continue
        MessageDispatcherJob(msg=msg).enqueue()
    return f"Message created and dispatched to {team.channel_teams.count()} channels"


class MessageCreatorJob(Job):
    """Instantiate a message and enqueues a `MessageDispatcherJob` for each subscribed channel."""

    def __init__(self, msg_class: Type[BaseMessage], team: Team, **kwargs):
        self.msg_class = msg_class
        self.team = team
        self.kwargs = kwargs

    def function_to_execute(self) -> Callable:
        return create_and_dispatch_message

    def get_kwargs(self) -> Dict:
        return {
            "msg_class": self.msg_class,
            "team": self.team,
            **self.kwargs,
        }

    def q_options(self) -> Dict[str, Any]:
        return {
            "cluster": "messages",
            "group": f"create {self.msg_class.__name__} {self.team}",
        }
