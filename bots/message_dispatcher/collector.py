from app_prime_league.models import Team
from bots.discord_interface.discord_bot import DiscordBot
from bots.message_dispatcher.dispatcher import MessageDispatcher
from bots.messages.base import BaseMessage
from bots.telegram_interface.telegram_bot import TelegramBot


class MessageCollector:

    def __init__(self, team: Team):
        self.team = team
        self.bots = []
        self._initialize()

    def _initialize(self):
        if self.team.telegram_id is not None:
            self.bots.append(TelegramBot)
        if self.team.discord_channel_id is not None:
            self.bots.append(DiscordBot)

    def dispatch(self, msg_class, **kwargs):
        assert issubclass(msg_class, BaseMessage)
        msg = msg_class(team=self.team, **kwargs)
        if not msg.team_wants_notification():
            return
        for bot in self.bots:
            MessageDispatcher(bot=bot, msg=msg, team=self.team).enqueue()
