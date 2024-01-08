from typing import Type

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.messages.base import BaseMessage


class NotificationToTeamMessage(BaseMessage):
    mentionable = True

    def __init__(self, team: Team, custom_message: str, **message_elements):
        super().__init__(team)
        self.custom_message = custom_message
        self._message_elements = message_elements
        self._generate_message()

    def _generate_title(self):
        return "🛠️ " + _("Developer notification")

    def _generate_message(self):
        # TODO i18n ?! Oder eher dann ins adminpanel auslagern
        return self.custom_message.format(team=self.team, **self._message_elements)


def validate_template(klass: Type[NotificationToTeamMessage], message_template: str, team=None, **message_elements):
    """
    Validates a template string for a given message class. Raises a ValidationError if the template is invalid.
    Returns the rendered message if the template is valid.
    """
    team = team or Team(name="A registered team", language="de")
    try:
        return klass(custom_message=message_template, team=team, **message_elements).generate_message()
    except ValueError as e:
        raise ValidationError(f"Invalid template formatting: {e}")
    except (AttributeError, KeyError) as e:
        raise ValidationError(f"Invalid attribute: {e}")
