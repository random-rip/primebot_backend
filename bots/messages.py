from abc import abstractmethod, ABC

from babel import dates as babel
from discord import Colour, Embed
from django.conf import settings

from app_prime_league.models import Match, Team, ScoutingWebsite
from bots.languages import de_DE as LaP
from modules.parsing.logs import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from utils.emojis import EMOJI_FIGHT, EMOJI_ARROW_RIGHT, EMOJI_CALENDAR, EMOJI_BOOKMARK, EMJOI_MAGN_GLASS, EMOJI_ONE, \
    EMOJI_TWO, EMOJI_THREE, EMOJI_FOUR, EMOJI_FIVE, EMOJI_SIX, EMOJI_SEVEN, EMOJI_EIGHT, EMOJI_NINE, EMOJI_TEN

emoji_numbers = [
    EMOJI_ONE,
    EMOJI_TWO,
    EMOJI_THREE,
    EMOJI_FOUR,
    EMOJI_FIVE,
    EMOJI_SIX,
    EMOJI_SEVEN,
    EMOJI_EIGHT,
    EMOJI_NINE,
    EMOJI_TEN,
]


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class BaseMessage:
    _key = None  # Message kann über die Settings gesteuert werden, ob sie gesendet wird, oder nicht
    mentionable = False  # Rollenerwähnung bei discord falls Rolle gesetzt
    title = None

    def __init__(self, team: Team, **kwargs):
        self.team = team
        self.message = None

    @abstractmethod
    def _generate_message(self):
        pass

    def generate_title(self):
        return self.title

    def team_wants_notification(self):
        key = type(self)._key
        if key is None:
            return True
        return self.team.value_of_setting(key)


class MatchMessage(BaseMessage, ABC):

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match

    @property
    def match_url(self):
        return f"{settings.MATCH_URI}{self.match.match_id}"

    @property
    def enemy_team_url(self):
        return f"{settings.TEAM_URI}{self.match.enemy_team_id}"

    @property
    def enemy_team_scouting_url(self):
        return self.team.get_scouting_url(match=self.match, lineup=False)

    @property
    def enemy_lineup_scouting_url(self):
        return self.team.get_scouting_url(match=self.match, lineup=True)

    @property
    def scouting_website(self):
        return settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name


class WeeklyNotificationMessage(MatchMessage):
    _key = "WEEKLY_MATCH_DAY"
    title = LaP.TITLE_NEW_MATCH_DAY
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self.message = None
        self._generate_message()

    def _generate_message(self):
        op_link = self.enemy_team_scouting_url
        if op_link is None:
            raise Exception()
        enemy_team_tag = self.match.enemy_team.team_tag
        self.message = LaP.WEEKLY_UPDATE_TEXT.format(
            match_day=self.match.match_day,
            match_url=self.match_url,
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            website=self.scouting_website,
            scouting_url=self.enemy_team_scouting_url,

        )


class NewMatchNotification(MatchMessage):
    """
    Teamaktualisierungen generieren keine Benachrichtigungen, deswegen ist die Message silenced.
    (Bisher gedacht für Kalibrierungsspiele, kann aber auf die Starterdivision ausgeweitet werden)
    """
    _key = "NEW_MATCH_NOTIFICATION"
    title = LaP.TITLE_NEW_MATCH
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self._generate_message()

    def _generate_message(self):
        self.message = LaP.NEXT_MATCH_IN_CALIBRATION.format(
            match_day=self.match.match_day,
            match_url=self.match_url,
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            website=self.scouting_website,
            scouting_url=self.enemy_team_scouting_url,
        )


class NewLineupNotificationMessage(MatchMessage):
    _key = "LINEUP_NOTIFICATION"
    title = LaP.TITLE_NEW_LINEUP
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self._generate_message()

    def _generate_message(self):
        self.message = LaP.NEW_LINEUP_TEXT.format(
            enemy_team_tag=self.match.enemy_team.team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match.match_day,
            match_url=self.match_url,
            scouting_url=self.enemy_lineup_scouting_url,
        )


class OwnNewTimeSuggestionsNotificationMessage(MatchMessage):
    _key = "TEAM_SCHEDULING_SUGGESTION"
    title = LaP.TITLE_NEW_OWN_SUGGESTION
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self._generate_message()

    def _generate_message(self):
        self.message = LaP.OWN_NEW_TIME_SUGGESTION_TEXT.format(
            match_day=self.match.match_day,
            match_url=self.match_url
        )


class EnemyNewTimeSuggestionsNotificationMessage(MatchMessage):
    _key = "ENEMY_SCHEDULING_SUGGESTION"
    title = LaP.TITLE_NEW_SUGGESTION
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self._generate_message()

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))
        enemy_team_tag = self.match.enemy_team.team_tag

        prefix = LaP.NEW_TIME_SUGGESTION_PREFIX if len(details) == 1 else LaP.NEW_TIME_SUGGESTIONS_PREFIX

        prefix += LaP.SUGGESTIONS.format(
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            match_day=self.match.match_day,
            match_url=self.match_url
        )

        self.message = prefix + '\n'.join(
            [f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])


class ScheduleConfirmationNotification(MatchMessage):
    _key = "SCHEDULING_CONFIRMATION"
    title = LaP.TITLE_MATCH_CONFIRMATION
    mentionable = True

    def __init__(self, team: Team, match: Match, latest_confirmation_log):
        super().__init__(team, match)
        self.latest_confirmation_log = latest_confirmation_log
        self._generate_message()

    def _generate_message(self):
        time = format_datetime(self.match.begin)
        enemy_team_tag = self.match.enemy_team.team_tag

        if isinstance(self.latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = LaP.AUTOMATIC + LaP.SCHEDULING_CONFIRMATION_TEXT
        elif isinstance(self.latest_confirmation_log, LogSchedulingConfirmation):
            message = LaP.SCHEDULING_CONFIRMATION_TEXT
        else:
            assert isinstance(self.latest_confirmation_log, LogChangeTime)
            message = LaP.MATCH_BEGIN_CHANGE_TEXT

        self.message = message.format(
            time=time,
            enemy_team_tag=enemy_team_tag,
            match_url=f"{settings.MATCH_URI}{self.match.match_id}",
            enemy_team_url=f"{settings.TEAM_URI}{self.match.enemy_team.id}",
            **vars(self.match))


class MatchesOverview(BaseMessage):
    _key = "overview"
    mentionable = False

    def __init__(self, team: Team, ):
        super().__init__(team)
        self._generate_message()

    def _generate_message(self):
        matches_to_play = self.team.get_open_matches_ordered()
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        if len(matches_to_play) == 0:
            self.message = LaP.NO_CURRENT_MATCHES
            return
        a = [
            f"[{LaP.MATCH_DAY} {match.match_day if match.match_day else LaP.TIEBREAKER}]({settings.MATCH_URI}{match.match_id}) {EMOJI_FIGHT} {match.enemy_team.name}" \
            f" {EMOJI_ARROW_RIGHT} [{website_name}]({match.team.get_scouting_url(match=match, lineup=False)})\n"
            for match in matches_to_play]
        matches_text = "\n".join(a)
        self.message = f"**{LaP.OVERVIEW}**\n\n" + matches_text

    def discord_embed(self):
        matches_to_play = self.team.get_open_matches_ordered()
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        embed = Embed(color=Colour.gold())
        if len(matches_to_play) == 0:
            embed.title = LaP.NO_CURRENT_MATCHES
        else:
            embed.title = LaP.OVERVIEW

        for match in matches_to_play:
            name = f"{EMOJI_FIGHT} "
            name += f"{LaP.MATCH_DAY} {match.match_day}" if match.match_day else f"{LaP.TIEBREAKER}"
            scouting_link = self.team.get_scouting_url(match=match, lineup=False)
            value = f"[{LaP.VS} {match.enemy_team.name}]({settings.MATCH_URI}{match.match_id})" \
                    f"\n> {EMJOI_MAGN_GLASS} [{website_name}]({scouting_link})"

            if not match.match_begin_confirmed:
                if match.team_made_latest_suggestion is None:
                    value += f"\n> {EMOJI_CALENDAR} Keine Terminvorschläge. " \
                             f"Ausweichtermin: {format_datetime(match.begin)}"
                if match.team_made_latest_suggestion is False:
                    value += f"\n> {EMOJI_CALENDAR}⚠ Offene Terminvorschläge vom Gegner!"
                if match.team_made_latest_suggestion is True:
                    value += f"\n> {EMOJI_CALENDAR}✅ Offene Terminvorschläge von euch."
            else:
                value += f"\n> {EMOJI_CALENDAR} {format_datetime(match.begin)}"

            if match.enemy_lineup_available:
                lineup_link = match.team.get_scouting_url(match=match, lineup=True)
                value += f"\n> {EMOJI_BOOKMARK} [{LaP.CURRENT_LINEUP}]({lineup_link})"

            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(
            text=f"Andere Scouting Website? mit `!settings` einfach anpassen.")
        return embed


class MatchOverview(MatchMessage):

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self.embed = Embed(color=Colour.gold())

    def _generate_message(self):
        self.message = ""

    def _add_schedule(self, ):
        name = "Termin"
        value = ""
        if self.match.match_begin_confirmed:
            value += f"> {EMOJI_CALENDAR} {format_datetime(self.match.begin)}\n"
        else:
            if self.match.team_made_latest_suggestion is None:
                value += (
                    f"> {EMOJI_CALENDAR} Keine Terminvorschläge. Ausweichtermin: "
                    f"{format_datetime(self.match.begin)}\n"
                )
            elif self.match.team_made_latest_suggestion is False:
                value += f"> {EMOJI_CALENDAR} ⚠ Offene Terminvorschläge vom Gegner!\n"
            else:
                value += f"> {EMOJI_CALENDAR} ✅ Offene Terminvorschläge von euch:\n"
            suggestions = self.match.suggestion_set.all()
            for i, x in enumerate(suggestions):
                value += f"> ➕ {emoji_numbers[i]} {format_datetime(x.begin)}\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_meta_information(self):
        text = (
            "> Ihr habt im **ersten** Spiel Seitenwahl.\n"
            "> Folgende Champions sind gesperrt:\n"
            "> ➕ ⛔️Renata Glasc\n"
            "> Das Regelwerk gibt es [hier.](https://www.primeleague.gg/statics/rules_general)\n"
        )

        self.embed.add_field(name="Sonstige Informationen", value=text, inline=False)

    def _add_enemy_team(self):
        name = "Gegnerteam"
        value = ""
        multi = ScoutingWebsite.objects.get_multi_websites()

        names = list(self.match.enemy_team.player_set.get_active_players().values_list("summoner_name", flat=True))
        for i in multi:
            value += (
                f"> {EMJOI_MAGN_GLASS} [{i.name}]({i.generate_url(names)})\n"
            )
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_enemy_players(self):
        name = f"Gegnerische Spieler (leagueofgraphs.com)"
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
        name = "Spielergebnis"
        value = ""
        value += f"ℹ️ Ergebnis: {self.match.result}\n"
        value += f"📆️ Gespielt: {format_datetime(self.match.begin)}\n"
        self.embed.add_field(name=name, value=value, inline=False)

    def _add_team_lineup(self, result=False):
        name = "Eure Aufstellung"
        value = ""
        if self.match.team_lineup_available:
            if not result:
                value += f"✅ Eigenes Lineup aufgestellt:\n"
            for i, x in enumerate(self.match.team_lineup.all()):
                value += f" > {emoji_numbers[i]} {x.summoner_name}\n"
        else:
            value += f"⚠ Noch kein Lineup aufgestellt.\n"
        self.embed.add_field(name=name, value=value)

    def _add_enemy_lineup(self, result=False):
        name = "Gegnerische Aufstellung"
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
            value += f"Noch kein Lineup aufgestellt.\n"
        self.embed.add_field(name=name, value=value)

    def _add_disclaimer(self):
        name = "Disclaimer"
        value = (
            "_Dieser Befehl befindet sich noch in der Beta! Wir sammeln dazu noch Feedback.\n"
            "Wie findet ihr die Menge an Informationsgehalten dieser Nachricht? Werden falsche Informationen angezeigt "
            "oder funktionieren Links nicht?\n"
            "Schreibt es uns hier: https://discord.gg/hBmHfF3K _"
        )
        self.embed.add_field(
            name=name,
            value=value,
            inline=False
        )

    def discord_embed(self):

        self._add_disclaimer()
        name = f"{EMOJI_FIGHT} "
        name += f"{LaP.MATCH_DAY} {self.match.match_day}" if self.match.match_type == Match.MATCH_TYPE_LEAGUE else f"{LaP.TIEBREAKER}"
        value = f"[{LaP.VS} {self.match.enemy_team.name}]({self.match_url})\n"
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
            self._add_meta_information()
        self.embed.set_footer(
            text=f"Andere Scouting Website? mit `!settings` einfach anpassen.")

        return self.embed


class NotificationToTeamMessage(BaseMessage):
    _key = "custom_message"
    mentionable = True
    title = "Entwicklerbenachrichtigung"

    def __init__(self, team: Team, custom_message, **kwargs):
        super().__init__(team, **kwargs)
        self.custom_message = custom_message
        self._generate_message()

    def _generate_message(self):
        self.message = self.custom_message.format(team=self.team)
