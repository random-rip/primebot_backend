from django.utils.translation import gettext as _

from app_prime_league.models import Match
from utils.utils import format_datetime


class MatchDisplayHelper:

    @staticmethod
    def display_match_day(match: Match) -> str:
        if match.match_day == Match.MATCH_DAY_PLAYOFF:
            msg = _("Playoff Match {match_day}")
        elif match.match_day == Match.MATCH_DAY_TIEBREAKER:
            msg = _("Tiebreaker Match {match_day}")
        elif match.match_type == Match.MATCH_TYPE_GROUP:
            msg = _("Match {match_day}")
        else:
            msg = _("Spieltag {match_day}")
        return msg.format(match_day=match.match_day)

    @staticmethod
    def display_match_schedule(match: Match) -> str:
        if match.match_begin_confirmed:
            return f"📆 {format_datetime(match.begin)}"

        if match.team_made_latest_suggestion is None:
            return "📆 " + _(
                "Keine Terminvorschläge. Ausweichtermin: {time}"
            ).format(
                time=format_datetime(match.begin)
            )
        if match.team_made_latest_suggestion is False:
            return "📆 ⚠ " + _("Offene Terminvorschläge vom Gegner!")
        if match.team_made_latest_suggestion is True:
            return "📆 ✅ " + _("Offene Terminvorschläge von euch.")
