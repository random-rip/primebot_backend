from typing import Any, Callable, Dict, Type

from app_prime_league.models import Team
from bots.base.bot_interface import BotInterface
from bots.discord_interface.discord_bot import DiscordBot
from bots.messages.base import BaseMessage
from bots.telegram_interface.telegram_bot import TelegramBot
from core.cluster_job import Job

from .dispatcher import MessageDispatcherJob


def create_and_dispatch_message(msg_class: Type[BaseMessage], team: Team, **kwargs):
    """
    Creates a message and enqueues a `MessageDispatcherJob` for each bot.
    """
    assert issubclass(msg_class, BaseMessage)
    msg = msg_class(team=team, **kwargs)
    if not msg.team_wants_notification():
        return "Team does not want notifications"

    platforms = []

    def dispatch_message(bot: Type[BotInterface]):
        MessageDispatcherJob(bot=bot, msg=msg).enqueue()
        platforms.append(bot.platform_name)

    if team.telegram_id is not None:
        dispatch_message(TelegramBot)
    if team.discord_channel_id is not None:
        dispatch_message(DiscordBot)
    return f"{msg} sent to {msg.team} on {', '.join(platforms)}" if platforms else "No platforms available"


class MessageCreatorJob(Job):
    """Creates a message (instantiate) and enqueues a `MessageDispatcherJob` for each bot."""

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
