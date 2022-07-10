from core.async_wrapper import AsyncWrapper


def dispatch(bot, msg, team):
    print(bot)
    print(msg)
    print(team)
    bot.send_message(msg=msg, team=team)


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

    def arguments(self):
        return self.bot, self.msg, self.team,

    def function_to_execute(self):
        return dispatch
