from abc import abstractmethod

import discord
from babel import dates as babel
from discord import Colour

from app_prime_league.models import Match, Team
from bots.languages import de_DE as LaP
from bots.telegram_interface.tg_singleton import emoji_numbers
from modules.parsing.html_parser import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from prime_league_bot import settings
from utils.emojis import EMOJI_FIGHT, EMOJI_ARROW_RIGHT, EMOJI_CALENDAR, EMOJI_BOOKMARK, EMJOI_MAGN_GLASS


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


class WeeklyNotificationMessage(BaseMessage):
    msg_type = "weekly_notification"
    _key = "weekly_op_link"
    _attachable_key = "pin_weekly_op_link"
    title = LaP.TITLE_NEW_MATCH_DAY
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._attachable = self.team.value_of_setting(self._attachable_key)
        self.message = None
        self._generate_message()

    def _generate_message(self):
        op_link = self.match.team.get_scouting_link(match=self.match, lineup=False)
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        enemy_team_tag = self.match.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = LaP.WEEKLY_UPDATE_TEXT.format(website_name=website_name, op_link=op_link,
                                                     enemy_team_tag=enemy_team_tag, **vars(self.match))


class NewMatchNotification(BaseMessage):
    msg_type = "new_game_notification"
    _key = "new_game_notification"
    title = LaP.TITLE_NEW_MATCH
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._generate_message()

    def _generate_message(self):
        op_link = self.team.get_scouting_link(match=self.match, lineup=False)
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        enemy_team_tag = self.match.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = LaP.NEXT_MATCH_IN_CALIBRATION.format(website_name=website_name, op_link=op_link,
                                                            enemy_team_tag=enemy_team_tag, **vars(self.match))


class NewLineupNotificationMessage(BaseMessage):
    msg_type = "new_lineup_notification"
    _key = "lineup_op_link"
    title = LaP.TITLE_NEW_LINEUP
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._generate_message()

    def _generate_message(self):
        op_link = self.match.team.get_scouting_link(match=self.match, lineup=True)
        enemy_team_tag = self.match.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = LaP.NEW_LINEUP_TEXT.format(op_link=op_link, enemy_team_tag=enemy_team_tag, **vars(self.match))


class NewLineupInCalibrationMessage(BaseMessage):
    msg_type = "new_lineup_in_calibration"
    title = LaP.TITLE_NEW_LINEUP
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._generate_message()

    def _generate_message(self):
        op_link = self.team.get_scouting_link(match=self.match, lineup=True)
        enemy_team_name = self.match.enemy_team.name
        if op_link is None:
            raise Exception()
        self.message = LaP.NEW_LINEUP_IN_CALIBRATION.format(op_link=op_link, enemy_team_name=enemy_team_name,
                                                            **vars(self.match))


class OwnNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "own_new_time_suggestion_notification"
    _key = "scheduling_suggestion"
    title = LaP.TITLE_NEW_OWN_SUGGESTION
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._generate_message()

    def _generate_message(self):
        self.message = LaP.OWN_NEW_TIME_SUGGESTION_TEXT.format(**vars(self.match))


class EnemyNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "enemy_new_time_suggestion_notification"
    _key = "scheduling_suggestion"
    title = LaP.TITLE_NEW_SUGGESTION
    mentionable = True

    def __init__(self, team: Team, match: Match):
        super().__init__(team)
        self.match = match
        self._generate_message()

    def _generate_message(self):
        details = list(self.match.suggestion_set.all().values_list("begin", flat=True))
        enemy_team_tag = self.match.enemy_team.team_tag

        if len(details) == 1:
            prefix = LaP.NEW_TIME_SUGGESTION_PREFIX
        else:
            prefix = LaP.NEW_TIME_SUGGESTIONS_PREFIX
        prefix = prefix.format(enemy_team_tag=enemy_team_tag, **vars(self.match))

        self.message = prefix + '\n'.join([f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])


class ScheduleConfirmationNotification(BaseMessage):
    msg_type = "schedule_confirmation_notification"
    _key = "scheduling_confirmation"
    title = LaP.TITLE_MATCH_CONFIRMATION
    mentionable = True

    def __init__(self, team: Team, match: Match, latest_confirmation_log):
        super().__init__(team)
        self.match = match
        self.latest_confirmation_log = latest_confirmation_log
        self._generate_message()

    def _generate_message(self):
        time = format_datetime(self.match.begin)
        enemy_team_tag = self.match.enemy_team.team_tag

        if isinstance(self.latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = LaP.SCHEDULING_AUTO_CONFIRMATION_TEXT
        elif isinstance(self.latest_confirmation_log, LogSchedulingConfirmation):
            message = LaP.SCHEDULING_CONFIRMATION_TEXT
        else:
            assert isinstance(self.latest_confirmation_log, LogChangeTime)
            message = LaP.MATCH_BEGIN_CHANGE_TEXT

        self.message = message.format(time=time, enemy_team_tag=enemy_team_tag, **vars(self.match))


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
            f"[{LaP.MATCH_DAY} {match.match_day if match.match_day else LaP.TIEBREAKER}]({LaP.GENERAL_MATCH_LINK}{match.match_id}) {EMOJI_FIGHT} {match.enemy_team.name}" \
            f" {EMOJI_ARROW_RIGHT} [{website_name}]({match.team.get_scouting_link(match=match, lineup=False)})\n"
            for match in matches_to_play]
        matches_text = "\n".join(a)
        self.message = f"**{LaP.OVERVIEW}**\n\n" + matches_text

    def discord_embed(self):
        matches_to_play = self.team.get_open_matches_ordered()
        website_name = settings.DEFAULT_SCOUTING_NAME if not self.team.scouting_website else self.team.scouting_website.name
        embed = discord.Embed(color=Colour.from_rgb(255, 255, 0))
        if len(matches_to_play) == 0:
            embed.title = LaP.NO_CURRENT_MATCHES
        else:
            embed.title = LaP.OVERVIEW

        for match in matches_to_play:
            name = f"{EMOJI_FIGHT} "
            name += f"{LaP.MATCH_DAY} {match.match_day}" if match.match_day else f"{LaP.TIEBREAKER}"
            scouting_link = match.team.get_scouting_link(match=match, lineup=True)
            value = f"[{LaP.VS} {match.enemy_team.name}]({LaP.GENERAL_MATCH_LINK}{match.match_id})" \
                    f"\n> {EMJOI_MAGN_GLASS} [{website_name}]({scouting_link})"

            if match.begin is not None:
                value += f"\n> {EMOJI_CALENDAR} {format_datetime(match.begin)}"

            if match.lineup_available:
                lineup_link = match.team.get_scouting_link(match=match, lineup=True)
                value += f"\n> {EMOJI_BOOKMARK} [{LaP.CURRENT_LINEUP}]({lineup_link})"

            embed.add_field(name=name, value=value, inline=False)
        # embed.set_footer(text="Hier könnte eure Werbung stehen.")
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