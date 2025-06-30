import datetime

from django.utils.translation import gettext as _

from app_prime_league.models import Match
from core.cluster_job import SendMessageToDevsJob


def fmt_dt(dt: datetime.datetime) -> str:
    """
    Formats a datetime object to a discord timestamp string.
    :param dt: datetime object
    :return: discord formatted timestamp string
    """
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:F>"


def fmt_rel_dt(dt: datetime.datetime) -> str:
    """
    Formats a datetime object to a discord relative timestamp string.
    :param dt: datetime object
    :return: discord formatted relative timestamp string
    """
    timestamp = int(dt.timestamp())
    return f"<t:{timestamp}:R>"


class MatchDisplayHelper:
    @staticmethod
    def display_match_day(match: Match) -> str:
        if match.match_day == Match.MATCH_DAY_PLAYOFF:
            msg = _("playoff match {match_day}")
        elif match.match_day == Match.MATCH_DAY_TIEBREAKER:
            msg = _("tiebreaker match {match_day}")
        elif match.match_type == Match.MatchType.GROUP:
            msg = _("match {match_day}")
        else:
            msg = _("gameday {match_day}")
        return msg.format(match_day=match.match_day)

    @staticmethod
    def display_match_schedule(match: Match) -> str:
        if match.match_begin_confirmed:
            return f"📆 {fmt_dt(match.begin)}"

        if match.team_made_latest_suggestion is None:
            return "📆 " + _("No dates proposed. Alternative date: {time}").format(time=fmt_dt(match.begin))

        if match.datetime_until_auto_confirmation is None:
            # Happens when a suggested time is in the past, so the suggestion_made_at is 0
            # https://www.primeleague.gg/leagues/matches/1100090-debakel-mit-tentakel-vs-team-fireblade-ragnarok
            SendMessageToDevsJob(f"Match {match.id} has no datetime_until_auto_confirmation").enqueue()
            return "📆 " + _("No dates proposed. Alternative date: {time}").format(time=fmt_dt(match.begin))

        if match.team_made_latest_suggestion:
            return "📆 ✅ " + _("Dates proposed by you are open. Left time: {left_time}").format(
                left_time=fmt_rel_dt(match.datetime_until_auto_confirmation),
            )
        else:
            return "📆 ⚠ " + _("Dates proposed by the opponent are open! Left time: {left_time}").format(
                left_time=fmt_rel_dt(match.datetime_until_auto_confirmation),
            )

    @staticmethod
    def display_match_schedule_simple(match: Match) -> str:
        if match.match_begin_confirmed:
            return _("⚔ Match begin confirmed")

        if match.team_made_latest_suggestion is None or match.datetime_until_auto_confirmation is None:
            return _("📆 No dates proposed")

        if match.team_made_latest_suggestion:
            return _("✅ Dates proposed by you are open")
        else:
            return _("⚠ Dates proposed by the opponent are open!")
