from discord import Embed, Colour
from django.conf import settings
from django.utils.translation import gettext as _

from app_prime_league.models import Team, Match, Champion, ScoutingWebsite
from bots.messages.base import MatchMessage, MessageNotImplementedError, emoji_numbers
from utils.emojis import EMJOI_MAGN_GLASS
from utils.utils import format_datetime


class MatchOverview(MatchMessage):

    def _generate_title(self) -> str:
        return "🔥 " + _('Matchübersicht')

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self.embed = Embed(color=Colour.gold())

    def _generate_message(self):
        raise MessageNotImplementedError()

    def _add_schedule(self, ):
        name = _("Termin")

        value = (
            "> {match_begin}\n"
        ).format(
            match_begin=self.helper.display_match_schedule(self.match),
        )

        if not self.match.match_begin_confirmed:
            for i, x in enumerate(self.match.suggestion_set.all()):
                value += f"> ➕ {emoji_numbers[i]} {format_datetime(x.begin)}\n"

        self.embed.add_field(name=name, value=value, inline=False)

    def _add_general_information(self):
        name = _("Sonstige Informationen")
        text = ""

        if self.match.has_side_choice:
            text += "> " + _('Ihr habt im **ersten** Match Seitenwahl') + ".\n"
        else:
            text += "> " + _('Ihr habt im **zweiten** Match Seitenwahl') + ".\n"

        banned = Champion.objects.get_banned_champions(self.match.begin)

        if banned.exists():
            text += "> " + _("Folgende Champions sind voraussichtlich beim Spieltermin gesperrt") + ":\n"
            for i in banned:
                text += (
                    "> ➕ ⛔️{name} ({until_patch_label} {until_patch})\n"
                ).format(
                    name=i.name,
                    until_patch_label=_('bis Patch'),
                    until_patch=i.banned_until_patch
                )

        text += f"> " + _('Das Regelwerk gibt es [hier.]') + "(https://www.primeleague.gg/statics/rules_general)\n"

        self.embed.add_field(name=name, value=text, inline=False)

    def _add_enemy_team(self):
        name = _("Gegnerteam")
        value = ""
        multi = ScoutingWebsite.objects.get_multi_websites()

        names = list(self.match.enemy_team.player_set.get_active_players().values_list("summoner_name", flat=True))
        for i in multi:
            value += (
                f"> {EMJOI_MAGN_GLASS} [{i.name}]({i.generate_url(names)})\n"
            )
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_enemy_players(self):
        name = _("Gegnerische Spieler (leagueofgraphs.com)")
        value = ""
        single = ScoutingWebsite.objects.filter(multi=False).first()
        if not single:
            return

        names = list(self.match.enemy_team.player_set.get_active_players().values_list("summoner_name", flat=True))
        for i, player in enumerate(names):
            value += (
                f"> {emoji_numbers[i]} {EMJOI_MAGN_GLASS} [{player}]({single.generate_url(player)})\n"
            )
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_results(self):
        name = _("Matchergebnis")
        value = ""
        value += f"ℹ️ " + _('Ergebnis') + ": {self.match.result}\n"
        value += f"📆️ " + _('Termin') + f": {format_datetime(self.match.begin)}\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_team_lineup(self, result=False):
        name = _("Eure Aufstellung")
        value = ""
        if self.match.team_lineup_available:
            if not result:
                value += "✅ " + _('Eigenes Lineup aufgestellt:') + "\n"
            for i, x in enumerate(self.match.team_lineup.all()):
                value += f" > {emoji_numbers[i]} {x.summoner_name}\n"
        else:
            value += f"⚠ " + _('Es wurde noch kein Lineup aufgestellt.') + "\n"
        self.embed.add_field(name=name, value=value)

    def _add_enemy_lineup(self, result=False):
        name = _("Gegnerische Aufstellung")
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

            for i, x in enumerate(names):
                value += f"> {emoji_numbers[i]} {x.summoner_name}\n"
        else:
            value += _('Es wurde noch kein Lineup aufgestellt.') + "\n"
        self.embed.add_field(name=name, value=value)

    def _add_disclaimer(self):
        name = _("Disclaimer")
        value = _(
            "Dieser Befehl befindet sich noch in der Beta! Wir sammeln dazu noch Feedback.\n"
            "Welche Informationen fehlen euch noch?\n"
            "[Schreibt es uns auf Discord!](https://discord.gg/7NYgT2uFPm)"
        )
        value = f"_{value}_"
        self.embed.add_field(
            name=name,
            value=value,
            inline=False
        )

    def _generate_discord_embed(self):

        self._add_disclaimer()
        name = "⚔ {match_day}".format(
            match_day=self.helper.display_match_day(self.match).title(),
        )
        value = _(
            "[gegen {enemy_team_name}]({match_url})"
        ).format(
            enemy_team_name=self.match.enemy_team.name,
            match_url=f"{settings.MATCH_URI}{self.match.match_id}",
        )
        value += "\n"

        self.embed.add_field(name=name, value=value, inline=False)

        if self.match.closed:
            self._add_results()
            self._add_team_lineup(result=True)
            self._add_enemy_lineup(result=True)
        else:
            self._add_schedule()
            self._add_enemy_team()
            self._add_enemy_players()
            self._add_team_lineup()
            self._add_enemy_lineup()
            self._add_general_information()
        self.embed.set_footer(
            text=_("Andere Scouting Website? mit `!settings` einfach anpassen."))

        return self.embed
