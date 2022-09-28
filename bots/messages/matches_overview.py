import discord
from discord import Embed, Colour
from django.conf import settings
from django.db.models import F
from django.utils.translation import gettext as _

from app_prime_league.models import Team
from bots.messages.base import BaseMessage


class MatchesOverview(BaseMessage):
    settings_key = "NEW_MATCHES_NOTIFICATION"
    mentionable = True

    def __init__(self, team: Team, match_ids=None):
        super().__init__(team)
        self.matches = self.__get_relevant_matches(match_ids)

    def _generate_title(self):
        return "🔥 " + _("New matches")

    def __get_relevant_matches(self, match_ids=None):
        if match_ids is None:
            return self.team.get_open_matches_ordered()
        else:
            return self.team.matches_against.filter(match_id__in=match_ids).order_by(
                F('match_day').asc(nulls_last=True))

    def _generate_message(self):
        if len(self.matches) == 0:
            return _("You currently have no open matches.")
        a = [
            (
                "[{match_day}]({match_url}) ⚔ {enemy_team_name} ➡ [{website}]({scouting_url})\n"
            ).format(
                match_day=self.helper.display_match_day(match).title(),
                match_url=f"{settings.MATCH_URI}{match.match_id}",
                enemy_team_name=match.get_enemy_team().name,
                website=self.scouting_website,
                scouting_url=match.team.get_scouting_url(match=match, lineup=False),
            )
            for match in self.matches]
        matches_text = "\n".join(a)
        return f"**" + _("An overview of your open matches:") + f"**\n\n{matches_text}"

    def _generate_discord_embed(self) -> discord.Embed:
        embed = Embed(color=Colour.gold())
        if len(self.matches) == 0:
            embed.title = _("You currently have no open matches.")
        else:
            embed.title = _("An overview of your open matches:")

        for match in self.matches:
            name = "⚔ {match_day}".format(
                match_day=self.helper.display_match_day(match).title(),
            )
            value = _(
                "[against {enemy_team_name}]({match_url})"
            ).format(
                enemy_team_name=match.get_enemy_team().name,
                match_url=f"{settings.MATCH_URI}{match.match_id}",
            )
            value += f"\n> 🔍 [{self.scouting_website}]({match.team.get_scouting_url(match=match, lineup=False)})"
            value += f"\n> {self.helper.display_match_schedule(match)}"

            if match.enemy_lineup_available:
                value += (
                        "\n> 📑 " + _("[Current lineup]({lineup_link})")
                ).format(
                    lineup_link=match.team.get_scouting_url(match=match, lineup=True)
                )

            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(
            text=_("Different scouting website? Use /settings to change it."))
        return embed
