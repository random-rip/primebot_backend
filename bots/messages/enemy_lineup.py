from discord import Color, Embed
from django.utils.translation import gettext as _

from app_prime_league.models import Match, Team
from bots.messages.base import MatchMessage


class NewLineupNotificationMessage(MatchMessage):
    settings_key = "LINEUP_NOTIFICATION"
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team=team, match=match)

    def _generate_title(self):
        return "📑 " + _("New lineup")

    def _generate_message(self):
        return _(
            "[{enemy_team_tag}]({enemy_team_url}) ([{match_day}]({match_url})) "
            "submitted a new [lineup]({scouting_url})."
        ).format(
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match_helper.display_match_day(self.match),
            match_url=self.match_url,
            scouting_url=self.enemy_lineup_scouting_url,
        )

    def _generate_discord_embed(self):
        embed = Embed(color=Color.gold())
        embed.add_field(name="", value=self._generate_message(), inline=False)
        match_day = self.match.match_day
        embed.set_footer(text=_(f"To get more information about the match, use /match {match_day}."))
        return embed
