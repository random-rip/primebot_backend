from django.utils.translation import gettext as _

from app_prime_league.models import Match
from utils.utils import format_datetime


class MatchDisplayHelper:

    @staticmethod
    def display_match_day(match: Match) -> str:
        if match.match_day == Match.MATCH_DAY_PLAYOFF:
            msg = _("playoff match {match_day}")
        elif match.match_day == Match.MATCH_DAY_TIEBREAKER:
            msg = _("tiebreaker match {match_day}")
        elif match.match_type == Match.MATCH_TYPE_GROUP:
            msg = _("match {match_day}")
        else:
            msg = _("gameday {match_day}")
        return msg.format(match_day=match.match_day)

    @staticmethod
    def display_match_schedule(match: Match) -> str:
        if match.match_begin_confirmed:
            return f"📆 {format_datetime(match.begin)}"

        if match.team_made_latest_suggestion is None:
            return "📆 " + _(
                "No dates proposed. Alternative date: {time}"
            ).format(
                time=format_datetime(match.begin)
            )
        if match.team_made_latest_suggestion is False:
            return "📆 ⚠ " + _("Dates proposed by the opponent are open!")
        if match.team_made_latest_suggestion is True:
            return "📆 ✅ " + _("Dates proposed by you are open.")
