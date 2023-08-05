from typing import List

from discord import Colour, Embed
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Champion, Match, ScoutingWebsite, Team
from bots.messages.base import MatchMessage
from utils.emojis import EMJOI_MAGN_GLASS
from utils.utils import format_datetime


class MatchOverview(MatchMessage):
    def _generate_title(self) -> str:
        return "🔥 " + _("Match overview")

    def __init__(
        self,
        team: Team,
        match: Match,
    ):
        super().__init__(team=team, match=match)
        self.embed = Embed(color=Colour.gold())

    def _generate_message(self):
        self.generate_discord_embed()
        result = ""

        for field in self.embed.fields:
            telegramized_field_value = self.telegramize_from_discord(field.value)

            result += f"*{field.name}*\n"
            result += f"{telegramized_field_value}\n"

        return result

    def telegramize_from_discord(self, value: str) -> str:
        result = value.replace("!]", "]")

        if result[0] == '_' and result[-1] == '_':
            result = result[1:-1]

        result = result.replace("**", "*")
        return result

    def _add_schedule(
        self,
    ):
        name = _("Date")

        value = ("> {match_begin}\n").format(
            match_begin=self.match_helper.display_match_schedule(self.match),
        )

        if not self.match.match_begin_confirmed:
            for i, x in enumerate(self.match.suggestion_set.all(), start=1):
                value += f"> ➕ {self._get_number_as_emojis(i)} {format_datetime(x.begin)}\n"

        self.embed.add_field(name=name, value=value, inline=False)

    def _add_general_information(self):
        name = _("Other information")
        text = ""

        if self.match.has_side_choice:
            text += "> " + _("You have a choice of sides in the **first** game") + ".\n"
        else:
            text += "> " + _("You have a choice of sides in the **second** game") + ".\n"

        banned = Champion.objects.get_banned_champions(self.match.begin)

        if banned.exists():
            text += "> " + _("The following champions are expected to be locked at the scheduled date") + ":\n"
            for i in banned:
                text += ("> ➕ ⛔️{name} ({until_patch_label} {until_patch})\n").format(
                    name=i.name, until_patch_label=_("until patch"), until_patch=i.banned_until_patch
                )

        text += "> " + _("The rulebook is available [here.]") + "(https://www.primeleague.gg/statics/rules_general)\n"

        self.embed.add_field(name=name, value=text, inline=False)

    def _add_enemy_team(self):
        name = _("Opposing team")
        value = ""
        multi = ScoutingWebsite.objects.get_multi_websites()

        names = list(
            self.match.get_enemy_team().player_set.get_active_players().values_list("summoner_name", flat=True)
        )
        for i in multi:
            value += f"> {EMJOI_MAGN_GLASS} [{i.name}]({i.generate_url(names)})\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_enemy_players(self):
        name = _("Opposing players (leagueofgraphs.com)")
        single = ScoutingWebsite.objects.filter(multi=False).first()
        if not single:
            return

        names = list(
            self.match.get_enemy_team()
            .player_set.get_active_players()
            .order_by("summoner_name")
            .values_list("summoner_name", flat=True)
        )

        if len(names) < 9:
            self.embed.add_field(name=name, value=self.__get_players_embed_value(names, single), inline=False)
            return

        split_at = (len(names) // 2) + 1
        names_first_part = names[:split_at]
        names_second_part = names[split_at:]

        self.embed.add_field(name=name, value=self.__get_players_embed_value(names_first_part, single), inline=True)
        self.embed.add_field(
            name=name,
            value=self.__get_players_embed_value(names_second_part, single, start_at=split_at + 1),
            inline=True,
        )

    def __get_players_embed_value(self, names: List[str], scouting_website: ScoutingWebsite, start_at: int = 1) -> str:
        value = ""
        for player in names:
            number = self._get_number_as_emojis(start_at)
            add_string = f"> {number} {EMJOI_MAGN_GLASS} [{player}]({scouting_website.generate_url(player)})\n"
            value += add_string
            start_at += 1
        return value

    def _add_results(self):
        name = _("Match result")
        value = ""
        value += "ℹ️ " + _("Result") + f": {self.match.result}\n"
        value += "📆️ " + _("Date") + f": {format_datetime(self.match.begin)}\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_team_lineup(self, result=False):
        name = _("Your lineup")
        value = ""
        if self.match.team_lineup_available:
            if not result:
                value += "✅ " + _("Own lineup submitted:") + "\n"
            for i, x in enumerate(self.match.team_lineup.all(), start=1):
                value += f" > {self._get_number_as_emojis(i)} {x.summoner_name}\n"
        else:
            value += "⚠ " + _("No lineup has been submitted yet.") + "\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_enemy_lineup(self, result=False):
        name = _("Lineup of opponent")
        value = ""
        if self.match.enemy_lineup_available:
            names = self.match.enemy_lineup.all()
            if not result:
                multi = ScoutingWebsite.objects.get_multi_websites()
                for i in multi:
                    value += (
                        f"> {EMJOI_MAGN_GLASS} [{i.name}]("
                        f"{i.generate_url(list(names.values_list('summoner_name', flat=True)))})\n"
                    )

            for i, x in enumerate(names, start=1):
                value += f"> {self._get_number_as_emojis(i)} {x.summoner_name}\n"
        else:
            value += _("No lineup has been submitted yet.") + "\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _generate_discord_embed(self):
        name = "⚔ {match_day}".format(
            match_day=self.match_helper.display_match_day(self.match).title(),
        )
        value = _("[against {enemy_team_name}]({match_url})").format(
            enemy_team_name=self.match.get_enemy_team().name,
            match_url=f"{settings.MATCH_URI}{self.match.match_id}",
        )
        value += "\n"

        self.embed.add_field(name=name, value=value, inline=False)

        if self.match.closed:
            self._add_results()
            if self.match.enemy_team is not None:
                self._add_team_lineup(result=True)
                self._add_enemy_lineup(result=True)
        else:
            self._add_schedule()
            if self.match.enemy_team is not None:
                self._add_enemy_team()
                self._add_enemy_players()
                self._add_team_lineup()
                self._add_enemy_lineup()
            self._add_general_information()
        self.embed.set_footer(text=_("If there are outdated scouting links just use /match again after 15 minutes."))

        return self.embed
