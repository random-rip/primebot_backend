from typing import Type

from app_prime_league.models import Team
from bots.discord_interface.discord_bot import DiscordBot
from bots.messages.base import BaseMessage
from bots.telegram_interface.telegram_bot import TelegramBot

from .dispatcher import MessageDispatcherJob


class MessageCollector:
    """
    This class is used to fire *message_sends* to different platforms.
    """

    def __init__(self, team: Team):
        self.team = team
        self.bots = []
        self._initialize()

    def _initialize(self):
        if self.team.telegram_id is not None:
            self.bots.append(TelegramBot)
        if self.team.discord_channel_id is not None:
            self.bots.append(DiscordBot)

    def dispatch(self, msg_class: Type[BaseMessage], **kwargs) -> None:
        """
        This method fires *message_sends* to all registered platforms via the `MessageDispatcherJob`.
        Args:
            msg_class: MessageClass to generate the message. This Class must inherit from ``BaseMessage``.
            **kwargs: Keyword arguments, that are passed to the constructor of the given `msg_class`.
        """
        assert issubclass(msg_class, BaseMessage)
        msg = msg_class(team=self.team, **kwargs)
        if not msg.team_wants_notification():
            return
        for bot in self.bots:
            MessageDispatcherJob(bot=bot, msg=msg, team=self.team).enqueue()
