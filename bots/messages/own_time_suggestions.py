from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage
from utils.utils import format_datetime


class OwnNewTimeSuggestionsNotificationMessage(MatchMessage):
    settings_key = "TEAM_SCHEDULING_SUGGESTION"
    mentionable = True

    def __init__(self, team: Team, match: Match,):
        super().__init__(team=team, match=match)

    def _generate_title(self):
        return "📆 " + _("New date proposed by you")

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))

        prefix = ngettext(
            "New date proposed by you for [{match_day}]({match_url}):",
            "New dates proposed by you for [{match_day}]({match_url}):",
            len(details)
        ).format(
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url
        )
        return prefix + "\n" + '\n'.join(
            [f"{self._get_number_as_emojis(i)}{format_datetime(x)}" for i, x in enumerate(details, start=1)])
