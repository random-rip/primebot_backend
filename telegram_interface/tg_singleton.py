import telepot
from babel import dates as babel

from app_prime_league.models import Game
from parsing.parser import LogSchedulingAutoConfirmation, LogSchedulingConfirmation, LogChangeTime
from prime_league_bot import settings
from telegram_interface.messages import NEW_TIME_SUGGESTION_PREFIX, NEW_TIME_SUGGESTIONS_PREFIX, GENERAL_MATCH_LINK, \
    SCHEDULING_AUTO_CONFIRMATION_TEXT, SCHEDULING_CONFIRMATION_TEXT, GAME_BEGIN_CHANGE_TEXT, NEW_LINEUP_TEXT, \
    WEEKLY_UPDATE_TEXT, GENERAL_TEAM_LINK, OWN_NEW_TIME_SUGGESTION_TEXT, NEXT_GAME_TEXT
from utils.constants import EMOJI_THREE, EMOJI_ONE, EMOJI_TWO, EMOJI_SUCCESS, EMOJI_FIGHT, EMOJI_SOON, \
    EMOJI_LINEUP

emoji_numbers = [
    EMOJI_ONE,
    EMOJI_TWO,
    EMOJI_THREE,
]
bot = telepot.Bot(token=settings.TELEGRAM_BOT_KEY)


def send_message(msg: str, chat_id: int = None):
    """
    Sends a Message using Markdown. If settings.DEBUG is True, overwrites the chat_id.
    """
    if settings.DEBUG or chat_id is None:
        chat_id = settings.DEFAULT_TELEGRAM_CHAT_ID
    bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="Markdown", disable_web_page_preview=True)


def format_datetime(x):
    return babel.format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de",
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))


class TelegramMessagesWrapper:

    @staticmethod
    def send_new_suggestion_of_enemies(game: Game):
        details = list(game.suggestion_set.all().values_list("game_begin", flat=True))
        if len(details) == 1:
            prefix = NEW_TIME_SUGGESTION_PREFIX
        else:
            prefix = NEW_TIME_SUGGESTIONS_PREFIX
        prefix = prefix.format(game.enemy_team.team_tag, GENERAL_TEAM_LINK, game.enemy_team.id, game.game_day,
                               GENERAL_MATCH_LINK, game.game_id)

        message = prefix + '\n'.join([f"{emoji_numbers[i]}{format_datetime(x)}" for i, x in enumerate(details)])

        send_message(msg=message, chat_id=game.team.telegram_channel_id)
        return

    @staticmethod
    def send_new_suggestion(game: Game):
        message = OWN_NEW_TIME_SUGGESTION_TEXT.format(
            game.game_day,
            GENERAL_MATCH_LINK,
            game.game_id,
            EMOJI_SUCCESS
        )
        send_message(msg=message, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_scheduling_confirmation(game: Game, latest_confirmation_log):
        time = format_datetime(game.game_begin)
        details = (
            game.enemy_team.team_tag,
            GENERAL_TEAM_LINK,
            game.enemy_team.id,
            game.game_day,
            GENERAL_MATCH_LINK,
            game.game_id,
            EMOJI_FIGHT,
            time
        )
        if isinstance(latest_confirmation_log, LogSchedulingAutoConfirmation):
            message = SCHEDULING_AUTO_CONFIRMATION_TEXT.format(*details)
        elif isinstance(latest_confirmation_log, LogSchedulingConfirmation):
            message = SCHEDULING_CONFIRMATION_TEXT.format(*details)
        else:
            assert isinstance(latest_confirmation_log, LogChangeTime)
            message = GAME_BEGIN_CHANGE_TEXT.format(*details)
        send_message(msg=message, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_new_lineup_of_enemies(game: Game, ):
        op_link = game.get_op_link_of_enemies(only_lineup=True)
        if op_link is None:
            raise Exception()
        message = NEW_LINEUP_TEXT.format(
            game.enemy_team.team_tag,
            GENERAL_TEAM_LINK,
            game.enemy_team.id,
            game.game_day,
            GENERAL_MATCH_LINK,
            game.game_id,
            op_link,
            EMOJI_LINEUP,
        )
        send_message(msg=message, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_new_game_day(game: Game):
        op_link = game.get_op_link_of_enemies(only_lineup=False)
        text = WEEKLY_UPDATE_TEXT.format(
            EMOJI_SOON,
            game.game_day,
            GENERAL_MATCH_LINK,
            game.game_id,
            game.enemy_team.team_tag,
            GENERAL_TEAM_LINK,
            game.enemy_team.id,
            op_link
        )
        send_message(msg=text, chat_id=game.team.telegram_channel_id)

    @staticmethod
    def send_next_game_day_after_registration(game: Game):
        op_link = game.get_op_link_of_enemies(only_lineup=False)
        text = NEXT_GAME_TEXT + WEEKLY_UPDATE_TEXT.format(
            EMOJI_SOON,
            game.game_day,
            GENERAL_MATCH_LINK,
            game.game_id,
            game.enemy_team.team_tag,
            GENERAL_TEAM_LINK,
            game.enemy_team.id,
            op_link
        )
        send_message(msg=text, chat_id=game.team.telegram_channel_id)
