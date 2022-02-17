from abc import abstractmethod, ABC

import discord
from babel import dates as babel
from discord import Colour
from django.conf import settings

from app_prime_league.models import Match, Team
from bots.languages import de_DE as LaP
from modules.parsing.logs import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from utils.emojis import EMOJI_FIGHT, EMOJI_ARROW_RIGHT, EMOJI_CALENDAR, EMOJI_BOOKMARK, EMJOI_MAGN_GLASS, EMOJI_ONE, \
    EMOJI_TWO, EMOJI_THREE


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class BaseMessage:
    _key = None
    mentionable = False
    title = None

    def __init__(self, team: Team, **kwargs):
        self.team = team
        self.message = None
        self._attachable = False

    @abstractmethod
    def _generate_message(self):
        pass

    def generate_title(self):
        return self.title

    def team_wants_notification(self):
        return self.team.value_of_setting(type(self)._key)

    def can_be_pinned(self):
        return self._attachable


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
    def team_scouting_url(self):
        return self.match.team.get_scouting_link(match=self.match, lineup=False)

    @property
    def lineup_scouting_url(self):
        return self.match.team.get_scouting_link(match=self.match, lineup=True)

    @property
    def scouting_website(self):
        return settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name


class WeeklyNotificationMessage(MatchMessage):
    msg_type = "weekly_notification"
    _key = "weekly_op_link"
    _attachable_key = "pin_weekly_op_link"
    title = LaP.TITLE_NEW_MATCH_DAY
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team, match)
        self._attachable = self.team.value_of_setting(self._attachable_key)
        self.message = None
        self._generate_message()

    def _generate_message(self):
        op_link = self.team_scouting_url
        if op_link is None:
            raise Exception()
        enemy_team_tag = self.match.enemy_team.team_tag
        self.message = LaP.WEEKLY_UPDATE_TEXT.format(
            match_day=self.match.match_day,
            match_url=self.match_url,
            enemy_team_tag=enemy_team_tag,
            enemy_team_url=self.enemy_team_url,
            website=self.scouting_website,
            scouting_url=self.team_scouting_url,

        )


class NewMatchNotification(MatchMessage):
    msg_type = "new_game_notification"
    _key = "new_game_notification"
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
            scouting_url=self.team_scouting_url,
        )


class NewLineupNotificationMessage(MatchMessage):
    msg_type = "new_lineup_notification"
    _key = "lineup_op_link"
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
            scouting_url=self.lineup_scouting_url,
        )


class OwnNewTimeSuggestionsNotificationMessage(MatchMessage):
    msg_type = "own_new_time_suggestion_notification"
    _key = "scheduling_suggestion"
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
    msg_type = "enemy_new_time_suggestion_notification"
    _key = "scheduling_suggestion"
    title = LaP.TITLE_NEW_SUGGESTION
    mentionable = True
    emoji_numbers = [
        EMOJI_ONE,
        EMOJI_TWO,
        EMOJI_THREE,
    ]

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
            [f"{self.emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])


class ScheduleConfirmationNotification(MatchMessage):
    msg_type = "schedule_confirmation_notification"
    _key = "scheduling_confirmation"
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
    msg_type = "overview"
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
            f" {EMOJI_ARROW_RIGHT} [{website_name}]({match.team.get_scouting_link(match=match, lineup=False)})\n"
            for match in matches_to_play]
        matches_text = "\n".join(a)
        self.message = f"**{LaP.OVERVIEW}**\n\n" + matches_text

    def discord_embed(self):
        matches_to_play = self.team.get_open_matches_ordered()
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        embed = discord.Embed(color=Colour.gold())
        if len(matches_to_play) == 0:
            embed.title = LaP.NO_CURRENT_MATCHES
        else:
            embed.title = LaP.OVERVIEW

        for match in matches_to_play:
            name = f"{EMOJI_FIGHT} "
            name += f"{LaP.MATCH_DAY} {match.match_day}" if match.match_day else f"{LaP.TIEBREAKER}"
            scouting_link = match.team.get_scouting_link(match=match, lineup=True)
            value = f"[{LaP.VS} {match.enemy_team.name}]({settings.MATCH_URI}{match.match_id})" \
                    f"\n> {EMJOI_MAGN_GLASS} [{website_name}]({scouting_link})"

            if not match.match_begin_confirmed:
                if match.team_made_latest_suggestion is None:
                    value += f"\n> {EMOJI_CALENDAR} Keine Terminvorschläge. " \
                             f"Standardtermin: {format_datetime(match.begin)}"
                if match.team_made_latest_suggestion is False:
                    value += f"\n> {EMOJI_CALENDAR}⚠ Offene Terminvorschläge vom Gegner!"
                if match.team_made_latest_suggestion is True:
                    value += f"\n> {EMOJI_CALENDAR}✅ Offene Terminvorschläge von euch."
            else:
                value += f"\n> {EMOJI_CALENDAR} {format_datetime(match.begin)}"

            if match.lineup_available:
                lineup_link = match.team.get_scouting_link(match=match, lineup=True)
                value += f"\n> {EMOJI_BOOKMARK} [{LaP.CURRENT_LINEUP}]({lineup_link})"

            embed.add_field(name=name, value=value, inline=False)
        embed.set_footer(
            text=f"Andere Scouting Website? mit `!settings` einfach anpassen.")
        return embed


class NotificationToTeamMessage(BaseMessage):
    msg_type = "custom_message"
    _key = "custom_message"
    mentionable = True
    title = "Entwicklerbenachrichtigung"

    def __init__(self, team: Team, custom_message, **kwargs):
        super().__init__(team, **kwargs)
        self.custom_message = custom_message
        self._generate_message()

    def _generate_message(self):
        self.message = self.custom_message.format(team=self.team)
