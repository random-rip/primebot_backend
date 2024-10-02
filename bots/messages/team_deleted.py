from django.utils.translation import gettext
from django.utils.translation import gettext as _

from bots.messages.base import BaseMessage


class TeamDeletedMessage(BaseMessage):
    mentionable = True

    def _generate_message(self) -> str:
        return gettext(
            "The registered team {team_name} has been deleted from the Prime League system. "
            "All information about this team and the link to the channel will be deleted."
        ).format(team=self.team.name)

    def _generate_title(self):
        return "🚫 " + _("Team deleted")
