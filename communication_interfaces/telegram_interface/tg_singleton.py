import logging

import telepot
from telegram import ParseMode

from app_prime_league.models import Game
from communication_interfaces.languages.de_DE import (
    WEEKLY_UPDATE_TEXT, MESSAGE_NOT_PINNED_TEXT, CANT_PIN_MSG_IN_PRIVATE_CHAT
)
from prime_league_bot import settings
from utils.constants import EMOJI_THREE, EMOJI_ONE, EMOJI_TWO

emoji_numbers = [
    EMOJI_ONE,
    EMOJI_TWO,
    EMOJI_THREE,
]
bot = telepot.Bot(token=settings.TELEGRAM_BOT_KEY)


def send_message(msg: str, chat_id: int = None, parse_mode=ParseMode.MARKDOWN, raise_again=False):
    """
    Sends a Message using Markdown as default.
    """
    if chat_id is None:
        chat_id = settings.DEFAULT_TELEGRAM_CHAT_ID
    try:
        return bot.sendMessage(chat_id=chat_id, text=msg, parse_mode=parse_mode, disable_web_page_preview=True)
    except Exception as e:
        logging.getLogger("notifications").exception(
            f"Error Sending Message in Chat chat_id={chat_id} msg={msg}\n{e}")
        if raise_again:
            raise e


def pin_msg(message) -> bool:
    message_id = message["message_id"]
    chat_id = message["chat"]["id"]
    try:
        return bot.pinChatMessage(chat_id=chat_id, message_id=message_id)
    except telepot.exception.NotEnoughRightsError:
        raise CannotBePinnedError()


class CannotBePinnedError(Exception):
    pass


# TODO: Restliche TelegramMessagesWrapper-Aufrufe refactoren
class TelegramMessagesWrapper:

    @staticmethod
    def send_next_game_day_after_registration(game: Game):
        op_link = game.get_op_link_of_enemies(only_lineup=False)
        text = WEEKLY_UPDATE_TEXT.format(op_link=op_link, enemy_team_tag=game.enemy_team.team_tag, **vars(game))
        message = send_message(msg=text, chat_id=game.team.telegram_id)
        try:
            pin_msg(message)
        except CannotBePinnedError:
            send_message(msg=MESSAGE_NOT_PINNED_TEXT, chat_id=game.team.telegram_id)
        except telepot.exception.TelegramError:
            logging.getLogger("notifications").exception(f"{game.team}: {CANT_PIN_MSG_IN_PRIVATE_CHAT}")
