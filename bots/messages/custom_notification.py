from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.messages.base import BaseMessage


class NotificationToTeamMessage(BaseMessage):
    mentionable = True

    def __init__(self, team: Team, custom_message, **kwargs):
        super().__init__(team, **kwargs)
        self.custom_message = custom_message
        self._generate_message()

    def _generate_title(self):
        return "🛠️ " + _("Developer notification")

    def _generate_message(self):
        # TODO i18n ?! Oder eher dann ins adminpanel auslagern
        return self.custom_message.format(team=self.team)
