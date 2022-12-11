from typing import Callable, Dict

from core.cluster_job import Job


def dispatch(bot, msg, team):
    bot.send_message(msg=msg, team=team)


class MessageDispatcherJob(Job):
    """
    Wrapper for creating an async task for Q cluster. Call `MessageDispatcher(Message).enqueue()` to
    create an async_task.
    """

    def function_to_execute(self) -> Callable:
        return dispatch

    __name__ = 'MessageDispatcher'

    def __init__(self, bot, msg, team):
        self.bot = bot
        self.msg = msg
        self.team = team

    def kwargs(self) -> Dict:
        """
        `q_options` and `task_name` are reserved keywords from `async_task`, so these keys cannot be used!
        Returns: Keyword arguments for the `function_to_execute`
        """
        return {
            "bot": self.bot,
            "msg": self.msg,
            "team": self.team,
        }

    def q_options(self):
        return {
            "timeout": 10,
        }
