import logging

import telepot
from telegram import ParseMode

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
