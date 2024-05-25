import logging
from typing import Callable, Dict

from bots.base.bot_interface import BotInterface
from bots.messages.base import BaseMessage
from core.cluster_job import Job

cluster_job_logger = logging.getLogger("cluster_job")


def send_message(bot: BotInterface, msg: BaseMessage):
    try:
        bot.send_message(msg=msg)
    except Exception as e:
        cluster_job_logger.exception(e)
        raise e


class MessageDispatcherJob(Job):
    """
    Wrapper for creating an async task for Q cluster. Call `MessageDispatcher(Message).enqueue()` to
    create an async_task.
    """

    __name__ = 'MessageDispatcher'

    def function_to_execute(self) -> Callable:
        return send_message

    def __init__(self, bot, msg):
        self.bot = bot
        self.msg = msg

    def kwargs(self) -> Dict:
        """
        `q_options` and `task_name` are reserved keywords from `async_task`, so these keys cannot be used!
        Returns: Keyword arguments for the `function_to_execute`
        """
        return {
            "bot": self.bot,
            "msg": self.msg,
        }

    def q_options(self):
        return {
            "timeout": 10,
            "group": str(self.msg),
        }
