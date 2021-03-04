from bots.bot import Bot


class TelegramBot(Bot):
    def register_team(self):
        config = {}
        return self._register_team(config)
