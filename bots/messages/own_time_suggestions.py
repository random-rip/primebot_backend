from django.utils.translation import gettext as _

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage


class OwnNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "TEAM_SCHEDULING_SUGGESTION"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)

    def _generate_title(self):
        return "📆 " + _('Eigener neuer Terminvorschlag')

    def _generate_message(self):
        return _(
            "Neuer Terminvorschlag von euch zu [{match_day}]({match_url}). ✅"
        ).format(
            match_day=self.helper.display_match_day(self.match),
            match_url=self.match_url
        )
