from abc import abstractmethod


class Bot:
    def __init__(self, *, bot, bot_config):
        self.bot = bot(**bot_config)
        self.token = bot_config.get("token")
        self._initialize()

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def _initialize(self):
        pass

    @staticmethod
    @abstractmethod
    def send_message(*, msg, team,):
        pass
