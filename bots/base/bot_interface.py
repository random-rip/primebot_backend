from abc import abstractmethod

from bots.messages.base import BaseMessage


class BotInterface:
    def __init__(self, *, bot, bot_config=None):
        bot_config = bot_config or {}
        self.bot = bot(**bot_config)
        self._token = bot_config.get("token", None)
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
