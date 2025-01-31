from typing import Type

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_prime_league.models import Channel
from bots.messages.base import ChannelMessage


class NotificationToChannelMessage(ChannelMessage):
    mentionable = False

    def __init__(self, channel: Channel, custom_message: str, **message_elements):
        super().__init__(channel)
        self.custom_message = custom_message
        self._message_elements = message_elements
        self._generate_message()

    def _generate_title(self):
        return "🛠️ " + _("Developer notification")

    def _generate_message(self):
        return self.custom_message.format(team=self.team, **self._message_elements)


def validate_template(klass: Type[NotificationToChannelMessage], message_template: str, **message_elements):
    """
    Validates a template string for a given message class. Raises a ValidationError if the template is invalid.
    Returns the rendered message if the template is valid.
    """
    channel = Channel()  # Create a dummy channel to pass to the message class
    try:
        return klass(custom_message=message_template, channel=channel, **message_elements).generate_message()
    except ValueError as e:
        raise ValidationError(f"Invalid template formatting: {e}")
    except (AttributeError, KeyError) as e:
        raise ValidationError(f"Invalid attribute: {e}")
