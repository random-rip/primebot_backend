from abc import abstractmethod

from babel import dates as babel

from app_prime_league.models import Game, Team
from communication_interfaces.languages.de_DE import WEEKLY_UPDATE_TEXT, NEW_LINEUP_TEXT, OWN_NEW_TIME_SUGGESTION_TEXT, \
    NEW_TIME_SUGGESTION_PREFIX, NEW_TIME_SUGGESTIONS_PREFIX, SCHEDULING_AUTO_CONFIRMATION_TEXT, \
    SCHEDULING_CONFIRMATION_TEXT, GAME_BEGIN_CHANGE_TEXT
from communication_interfaces.telegram_interface.tg_singleton import emoji_numbers
from parsing.parser import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from prime_league_bot import settings
from utils.constants import EMOJI_SOON


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class BaseMessage:
    def __init__(self, team: Team):
        self.team = team
        self.message = None

    @abstractmethod
    def _generate_message(self):
        pass


class WeeklyNotificationMessage(BaseMessage):
    msg_type = "weekly_notification"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        op_link = self.game.get_op_link_of_enemies(only_lineup=False)
        enemy_team_tag = self.game.enemy_team.team_tag
        if op_link is None:
            raise Exception()
        self.message = WEEKLY_UPDATE_TEXT.format(op_link=op_link, enemy_team_tag=enemy_team_tag, **vars(self.game))


class NewLineupNotificationMessage(BaseMessage):
    msg_type = "new_lineup_notification"

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


class OwnNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "own_new_time_suggestion_notification"

    def __init__(self, team: Team, game: Game):
        super().__init__(team)
        self.game = game
        self._generate_message()

    def _generate_message(self):
        self.message = OWN_NEW_TIME_SUGGESTION_TEXT.format(**vars(self.game))


class EnemyNewTimeSuggestionsNotificationMessage(BaseMessage):
    msg_type = "enemy_new_time_suggestion_notification"

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
