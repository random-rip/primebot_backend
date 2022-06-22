from django.utils.translation import gettext as _

from app_prime_league.models import Team, Match
from bots.messages.base import MatchMessage


class NewLineupNotificationMessage(MatchMessage):
    settings_key = "LINEUP_NOTIFICATION"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)

    def _generate_title(self):
        return "📑 " + _('Neues Lineup')

    def _generate_message(self):
        return _(
            "[{enemy_team_tag}]({enemy_team_url}) ([{match_day}]({match_url})) hat ein neues "
            "[Lineup]({scouting_url}) aufgestellt."
        ).format(
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.helper.display_match_day(self.match),
            match_url=self.match_url,
            scouting_url=self.enemy_lineup_scouting_url,
        )
