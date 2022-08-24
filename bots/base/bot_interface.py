from abc import abstractmethod

from bots.messages.base import BaseMessage


class BotInterface:
    def __init__(self, *, bot, bot_config):
        self.bot = bot(**bot_config)
        self.token = bot_config.get("token")
        self._initialize()

    @abstractmethod
    def run(self):
        pass

    def _initialize(self):
        pass

    @staticmethod
    @abstractmethod
    def send_message(*, msg: BaseMessage, team, ):
        pass
