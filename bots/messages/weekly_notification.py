from django.utils.translation import gettext as _

from app_prime_league.models import Match, Team
from bots.messages.base import MatchMessage


class WeeklyNotificationMessage(MatchMessage):
    settings_key = "WEEKLY_MATCH_DAY"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team=team, match=match)

    def _generate_title(self):
        return "🌟 " + _("Weekly overview")

    def _generate_message(self) -> str:
        op_link = self.enemy_team_scouting_url
        if op_link is None:
            raise Exception(f"HOW THE FUCK IS the op_link None? This is illegal! {self.match.enemy_team}")
        enemy_team_tag = self.match.enemy_team.team_tag
        return _(
            "The next gameday:\n"
            "[{match_day}]({match_url}) against [{enemy_team_tag}]({enemy_team_url}):\n"
            "Here is your [{website} link]({scouting_url}) of the team."
        ).format(
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url,
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            website=self.scouting_website,
            scouting_url=self.enemy_team_scouting_url,
        )
