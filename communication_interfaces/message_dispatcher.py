from app_prime_league.models import Team
from communication_interfaces.discord_interface.discord_bot import DiscordBot
from communication_interfaces.messages import BaseMessage
from communication_interfaces.telegram_interface.telegram_bot import TelegramBot


class MessageDispatcher:

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
            pass
            # bot.send_message(msg=msg, team=self.team)

    def dispatch_raw_message(self, msg, **kwargs):
        for bot in self.bots:
            bot.send_message(msg=msg, team=self.team, )
