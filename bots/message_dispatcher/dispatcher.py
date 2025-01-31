import logging
from typing import Callable, Dict

from app_prime_league.models.channel import Platforms
from bots.discord_interface.discord_bot import DiscordBot
from bots.messages.base import BaseMessage
from bots.telegram_interface.telegram_bot import TelegramBot
from core.cluster_job import Job

cluster_job_logger = logging.getLogger("cluster_job")


def send_message(msg: BaseMessage):
    if not msg.team_wants_notification():
        return "Team does not want notifications"
    if msg.channel.platform == Platforms.DISCORD:
        DiscordBot.send_message(msg=msg)
        msg.discord_hooks()
    elif msg.channel.platform == Platforms.TELEGRAM:
        TelegramBot.send_message(msg=msg)
    else:
        raise NotImplementedError(f"No implementation for {msg.channel.platform}")
    return f"{msg} sent to {msg.team} on {msg.channel.platform}"


class MessageDispatcherJob(Job):
    """
    Enqueues a message to the correct platform.
    """

    __name__ = 'MessageDispatcher'

    def function_to_execute(self) -> Callable:
        return send_message

    def __init__(self, msg: BaseMessage):
        self.msg = msg

    def get_kwargs(self) -> Dict:
        """
        `q_options` and `task_name` are reserved keywords from `async_task`, so these keys cannot be used!
        Returns: Keyword arguments for the `function_to_execute`
        """
        return {
            "msg": self.msg,
        }

    def q_options(self):
        return {
            "timeout": 10,
            "group": f"dispatch {self.msg} {self.msg.team}",
            "cluster": "messages",
        }
