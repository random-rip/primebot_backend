from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.messages import MatchesOverview


class WeeklyNotificationMessage(MatchesOverview):
    settings_key = "WEEKLY_MATCH_DAY"
    mentionable = True

    def __init__(self, team: Team):
        super().__init__(team=team, match_ids=None)

    def _get_relevant_matches(self, team: Team, match_ids=None):
        lower_bound = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        upper_bound = lower_bound + timedelta(days=7)
        return team.get_open_matches_ordered().filter(begin__gte=lower_bound, begin__lte=upper_bound)

    def header(self) -> str:
        return _("The following matches are scheduled this week:")

    def no_matches_found(self) -> str:
        return _("You have no matches this week.")

    def _generate_title(self):
        return "🌟 " + _("Weekly overview")

    def team_wants_notification(self):
        if self.team.id == 105959:
            return True
        return False  # FIXME: As a workaround, we disable the notification for now
