from abc import abstractmethod

from babel import dates as babel

from app_prime_league.models import Game, Team
from communication_interfaces.languages.de_DE import WEEKLY_UPDATE_TEXT, NEW_LINEUP_TEXT, OWN_NEW_TIME_SUGGESTION_TEXT, \
    NEW_TIME_SUGGESTION_PREFIX, NEW_TIME_SUGGESTIONS_PREFIX, SCHEDULING_AUTO_CONFIRMATION_TEXT, \
    SCHEDULING_CONFIRMATION_TEXT, GAME_BEGIN_CHANGE_TEXT, NEXT_GAME_IN_CALIBRATION, NEW_LINEUP_IN_CALIBRATION, \
    GENERAL_MATCH_LINK
from communication_interfaces.telegram_interface.tg_singleton import emoji_numbers
from parsing.parser import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from prime_league_bot import settings
from utils.constants import EMOJI_FIGHT, EMOJI_ARROW_RIGHT


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class BaseMessage:
    _key = None

    def __init__(self, team: Team, **kwargs):
        self.team = team
        self.message = None
        self._attachable = False

    @abstractmethod
    def _generate_message(self):
        pass

    def notification_wanted(self):
        return self.team.value_of_setting(type(self)._key)

    def can_be_pinned(self):
        return self._attachable


class WeeklyNotificationMessage(BaseMessage):
    msg_type = "weekly_notification"
    _key = "weekly_op_link"
    _attachable_key = "pin_weekly_op_link"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._attachable = self.team.value_of_setting(self._attachable_key)
        self._generate_message()

    def _generate_message(self):
        op_link = self.game.get_op_link_of_enemies(only_lineup=False)
        enemy_team_tag = self.game.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = WEEKLY_UPDATE_TEXT.format(op_link=op_link, enemy_team_tag=enemy_team_tag, **vars(self.game))


class NewGameNotification(BaseMessage):
    msg_type = "new_game_notification"
    _key = "new_game_notification"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        op_link = self.game.get_op_link_of_enemies(only_lineup=False)
        enemy_team_tag = self.game.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = NEXT_GAME_IN_CALIBRATION.format(op_link=op_link, enemy_team_tag=enemy_team_tag,
                                                       **vars(self.game))


class NewLineupNotificationMessage(BaseMessage):
    msg_type = "new_lineup_notification"
    _key = "lineup_op_link"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        op_link = self.game.get_op_link_of_enemies(only_lineup=True)
        enemy_team_tag = self.game.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = NEW_LINEUP_TEXT.format(op_link=op_link, enemy_team_tag=enemy_team_tag, **vars(self.game))


class NewLineupInCalibrationMessage(BaseMessage):
    msg_type = "new_lineup_in_calibration"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        op_link = self.game.get_op_link_of_enemies(only_lineup=True)
        enemy_team_name = self.game.enemy_team.name
        if op_link is None:
            raise Exception()
        self.message = NEW_LINEUP_IN_CALIBRATION.format(op_link=op_link, enemy_team_name=enemy_team_name,
                                                        **vars(self.game))


class OwnNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "own_new_time_suggestion_notification"
    _key = "scheduling_suggestion"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        self.message = OWN_NEW_TIME_SUGGESTION_TEXT.format(**vars(self.game))


class EnemyNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "enemy_new_time_suggestion_notification"
    _key = "scheduling_suggestion"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        details = list(self.game.suggestion_set.all().values_list("game_begin", flat=True))
        enemy_team_tag = self.game.enemy_team.team_tag

        if len(details) == 1:
            prefix = NEW_TIME_SUGGESTION_PREFIX
        else:
            prefix = NEW_TIME_SUGGESTIONS_PREFIX
        prefix = prefix.format(enemy_team_tag=enemy_team_tag, **vars(self.game))

        self.message = prefix + '\n'.join([f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])


class ScheduleConfirmationNotification(BaseMessage):
    msg_type = "schedule_confirmation_notification"
    _key = "scheduling_confirmation"

    def __init__(self, team: Team, game: Game, latest_confirmation_log):
        super().__init__(team)
        self.game = game
        self.latest_confirmation_log = latest_confirmation_log
        self._generate_message()

    def _generate_message(self):
        time = format_datetime(self.game.game_begin)
        enemy_team_tag = self.game.enemy_team.team_tag

        if isinstance(self.latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = SCHEDULING_AUTO_CONFIRMATION_TEXT
        elif isinstance(self.latest_confirmation_log, LogSchedulingConfirmation):
            message = SCHEDULING_CONFIRMATION_TEXT
        else:
            assert isinstance(self.latest_confirmation_log, LogChangeTime)
            message = GAME_BEGIN_CHANGE_TEXT

        self.message = message.format(time=time, enemy_team_tag=enemy_team_tag, **vars(self.game))


class GamesOverview(BaseMessage):
    msg_type = "overview"
    _key = "overview"

    def __init__(self, team: Team, ):
        super().__init__(team)
        self._generate_message()

    def _generate_message(self):
        games_to_play = self.team.games_against.filter(game_closed=False).order_by("game_day")
        if len(games_to_play) == 0:
            self.message = "Ihr habt aktuell keine offenen Spiele."
            return
        a = [
            f"[Spieltag {game.game_day}]({GENERAL_MATCH_LINK}{game.game_id}) {EMOJI_FIGHT} {game.enemy_team.name} {EMOJI_ARROW_RIGHT} [OP.gg]({game.get_op_link_of_enemies(only_lineup=False)})\n"
            for game in games_to_play]
        games_text = "\n".join(a)
        self.message = "**Eine Übersicht eurer offenen Spiele:**\n\n" + games_text
