import discord
from discord import Embed, Colour
from django.conf import settings
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
        return "🔥 " + _('Neue Matches')

    def __get_relevant_matches(self, match_ids=None):
        if match_ids is None:
            return self.team.get_open_matches_ordered()
        else:
            return self.team.matches_against.filter(match_id__in=match_ids)

    def _generate_message(self):
        if len(self.matches) == 0:
            return _("Ihr habt aktuell keine offenen Matches.")
        a = [
            (
                "[{match_day}]({match_url}) ⚔ {enemy_team_name} ➡ [{website}]({scouting_url})\n"
            ).format(
                match_day=self.helper.display_match_day(match),
                match_url=f"{settings.MATCH_URI}{match.match_id}",
                enemy_team_name=match.enemy_team.name,
                website=self.scouting_website,
                scouting_url=match.team.get_scouting_url(match=match, lineup=False),
            )
            for match in self.matches]
        matches_text = "\n".join(a)
        return f"**" + _('Eine Übersicht eurer offenen Matches:') + f"**\n\n{matches_text}"

    def _generate_discord_embed(self) -> discord.Embed:
        embed = Embed(color=Colour.gold())
        if len(self.matches) == 0:
            embed.title = _("Ihr habt aktuell keine offenen Matches.")
        else:
            embed.title = _("Eine Übersicht eurer offenen Matches:")

        for match in self.matches:
            name = "⚔ {match_day}".format(
                match_day=self.helper.display_match_day(match),
            )
            value = _(
                "[gegen {enemy_team_name}]({match_url})"
            ).format(
                enemy_team_name=match.enemy_team.name,
                match_url=f"{settings.MATCH_URI}{match.match_id}",
            )
            value += f"\n> 🔍 [{self.scouting_website}]({match.team.get_scouting_url(match=match, lineup=False)})"
            value += f"\n> {self.helper.display_match_schedule(match)}"

            if match.enemy_lineup_available:
                value += (
                        f"\n> 📑 " + _('[Aktuelles Lineup]({lineup_link})')
                ).format(
                    lineup_link=match.team.get_scouting_url(match=match, lineup=True)
                )

            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(
            text=_("Andere Scouting Website? mit `!settings` einfach anpassen."))
        return embed
