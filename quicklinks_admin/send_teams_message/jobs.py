import logging
from typing import Any, Callable, Dict

from django.conf import settings

from app_prime_league.models import Channel
from bots.message_dispatcher import MessageDispatcherJob
from bots.messages import NotificationToChannelMessage
from core.cluster_job import Job
from core.github import GitHub


class VersionUpdateMessage(NotificationToChannelMessage):
    template = """Hallo Team(s),

🔥 Version {github.version} ist draußen 🔥

{github.body}

Alle weiteren Änderungen findet ihr auf unserer Website: {website}/information/changelog

Sternige Grüße
– PrimeBot devs
"""

    def __init__(self, channel: Channel, custom_message=None, **message_elements):
        super().__init__(
            channel=channel,
            custom_message=custom_message or self.template,
            **message_elements,
        )


def create_and_dispatch_message_to_channel(msg_class: type[VersionUpdateMessage], channel: Channel, **kwargs):
    """
    Creates a message and enqueues a `MessageDispatcherJob` for each subscribed channel
    """
    assert issubclass(msg_class, VersionUpdateMessage)
    msg = msg_class(channel=channel, **kwargs)
    MessageDispatcherJob(msg=msg).enqueue()
    return f"Message created and dispatched to Channel {channel}"


def enqueue_messages(message_template: str, channel_ids: list[int] = None):
    """
    Enqueues a version update message to all registered teams or a subset of registered teams.
    Recursively enqueues the message for failed teams.
    :param message_template: The message template to send
    :param channel_ids: A list of primary keys of the channels to send the message to
    """
    channels = Channel.objects.all()
    if channel_ids:
        channels = channels.filter(
            id__in=channel_ids,
        )
    github = GitHub.latest_version()
    for channel in channels:
        try:
            create_and_dispatch_message_to_channel(
                msg_class=VersionUpdateMessage,
                channel=channel,
                custom_message=message_template,
                github=github,
                website=settings.SITE_ID,
            )
        except Exception as e:
            logger = logging.getLogger("notifications")
            logger.exception(e)
            continue


class EnqueueMessagesJob(Job):
    """
    Enqueues a version update message to all channels or a subset of channels.
    """

    __name__ = 'EnqueueMessage'

    def function_to_execute(self) -> Callable:
        return enqueue_messages

    def __init__(self, message_template, channel_ids: list[int] = None):
        self.message_template = message_template
        self.channel_ids = channel_ids

    def get_kwargs(self) -> dict:
        return {
            "message_template": self.message_template,
            "channel_ids": self.channel_ids,
        }

    def q_options(self) -> Dict[str, Any]:
        return {
            "cluster": "messages",
            "group": "enqueue_messages",
        }
