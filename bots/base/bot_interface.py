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
    def send_message(*, msg: BaseMessage):
        """
        This method is designed to send non-interactive messages. This is usually triggered by prime league updates.
        To send a message from a user triggered action (f.e. a reply message), use context based messages
        directly. This is different for each of the communication platforms.
        """
        pass

    def __repr__(self):
        return self.__class__.__name__
