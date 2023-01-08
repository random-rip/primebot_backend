from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage
from core.parsing.logs import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from utils.utils import format_datetime


class ScheduleConfirmationNotification(MatchMessage):
    settings_key = "SCHEDULING_CONFIRMATION"
    mentionable = True

    def __init__(self, team: Team, match: Match, latest_confirmation_log):
        super().__init__(team=team, match=match)
        self.latest_confirmation_log = latest_confirmation_log

    def _generate_title(self):
        return "⚔ " + _("Confirmation of the scheduled date")

    def _generate_message(self):
        time = format_datetime(self.match.begin)
        enemy_team_tag = self.match.enemy_team.team_tag

        if isinstance(self.latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = _(
                "Automatic confirmation of the scheduled date against [{enemy_team_tag}]"
                "({enemy_team_url}) for [{match_day}]({match_url}):"
            )
        elif isinstance(self.latest_confirmation_log, LogSchedulingConfirmation):
            message = _(
                "Confirmation of the scheduled date against [{enemy_team_tag}]"
                "({enemy_team_url}) for [{match_day}]({match_url}):"
            )
        else:
            assert isinstance(self.latest_confirmation_log, LogChangeTime)
            message = _(
                "An administrator has set a new date for [{match_day}]({match_url}) "
                "against [{enemy_team_tag}]({enemy_team_url}):"
            )

        return (message + "\n⚔{time}").format(
            time=time,
            enemy_team_tag=enemy_team_tag,
            match_url=f"{settings.MATCH_URI}{self.match.match_id}",
            enemy_team_url=f"{settings.TEAM_URI}{self.match.enemy_team.id}",
            match_day=self.match_helper.display_match_day(self.match),
        )
