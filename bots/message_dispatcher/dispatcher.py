from core.async_wrapper import AsyncWrapper


class MessageDispatcher(AsyncWrapper):
    """
    Wrapper for creating an async task for Q cluster. Call `MessageDispatcher(Message).enqueue()` to
    create an async_task.
    """
    __name__ = 'MessageDispatcher'

    def __init__(self, bot, msg, team):
        self.bot = bot
        self.msg = msg
        self.team = team

    def _process(self):
        self.bot.send_message(msg=self.msg, team=self.team)
