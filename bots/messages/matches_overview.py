import discord
from discord import Colour, Embed
from django.db.models import F
from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.messages.base import MatchesMessage


class MatchesOverview(MatchesMessage):
    settings_key = "NEW_MATCHES_NOTIFICATION"
    mentionable = True

    def __init__(self, team: Team, match_ids: list = None):
        matches = self._get_relevant_matches(team, match_ids)
        super().__init__(team=team, matches=matches)

    def _get_relevant_matches(self, team: Team, match_ids=None):
        if match_ids is None:
            return team.get_open_matches_ordered()
        else:
            return team.matches_against.filter(match_id__in=match_ids).order_by(F('match_day').asc(nulls_last=True))

    def _generate_title(self):
        return "🔥 " + _("New matches")

    def header(self) -> str:
        return _("An overview of your open matches:")

    def no_matches_found(self):
        return _("You currently have no open matches.")

    def format_match(self, match) -> str:
        return ("[{match_day}]({match_url}) ⚔ {enemy_team_name} ➡ [{website}]({scouting_url})").format(
            match_day=self.match_helper.display_match_day(match).title(),
            match_url=self.get_match_url(match),
            enemy_team_name=match.get_enemy_team().name,
            website=self.scouting_website,
            scouting_url=self.get_enemy_team_scouting_url(match),
        )

    def _generate_discord_embed(self) -> discord.Embed:
        embed = Embed(color=Colour.gold())
        if len(self.matches) == 0:
            embed.title = self.no_matches_found()
        else:
            embed.title = self.header()

        for match in self.matches:
            name = "⚔ {match_day}".format(
                match_day=self.match_helper.display_match_day(match).title(),
            )
            value = _("[against {enemy_team_name}]({match_url})").format(
                enemy_team_name=match.get_enemy_team().name,
                match_url=self.get_match_url(match),
            )
            value += f"\n> 🔍 [{self.scouting_website}]({self.get_enemy_team_scouting_url(match)})"
            value += f"\n> {self.match_helper.display_match_schedule(match)}"

            if match.enemy_lineup_available:
                value += ("\n> 📑 " + _("[Current lineup]({lineup_link})")).format(
                    lineup_link=self.get_enemy_lineup_scouting_url(match)
                )

            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(
            text=_("The bot is currently deactivated as it no longer receives updates from the Prime League.")
        )
        return embed
