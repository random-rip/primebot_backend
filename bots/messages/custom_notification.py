from django.utils.translation import gettext as _

from bots.messages.base import BaseMessage


class NotificationToTeamMessage(BaseMessage):
    mentionable = True

    def __init__(self, team_id: int, custom_message: str, **kwargs):
        super().__init__(team_id, **kwargs)
        self.custom_message = custom_message
        self._generate_message()

    def _generate_title(self):
        return "🛠️ " + _("Developer notification")

    def _generate_message(self):
        # TODO i18n ?! Oder eher dann ins adminpanel auslagern
        return self.custom_message.format(team=self.team)
