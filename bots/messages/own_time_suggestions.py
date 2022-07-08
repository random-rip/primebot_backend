from django.utils.translation import gettext as _

from bots.messages.base import MatchMessage


class OwnNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "TEAM_SCHEDULING_SUGGESTION"
    mentionable = True

    def __init__(self, team_id: int, match_id: int):
        super().__init__(team_id=team_id, match_id=match_id)

    def _generate_title(self):
        return "📆 " + _("New date proposed by you")

    def _generate_message(self):
        return _(
            "New date proposed by you for [{match_day}]({match_url})."
        ).format(
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url
        )
