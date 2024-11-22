import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from telegram import Bot, ParseMode, TelegramError
from telegram.error import BadRequest, ChatMigrated, Unauthorized

notifications_logger = logging.getLogger("notifications")


def send_message_to_devs(msg: str, code: str = None, parse_mode=ParseMode.HTML):
    if code:
        msg = f"{msg}\n<code>{code}</code>"
    try:
        send_message(msg=msg, chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=parse_mode)
    except Exception as e:
        notifications_logger.exception(e)


async def asend_message_to_devs(msg, parse_mode=ParseMode.HTML):
    await sync_to_async(send_message_to_devs)(msg=msg, parse_mode=parse_mode, code=None)


def send_message(msg: str, chat_id: int, parse_mode=ParseMode.MARKDOWN, raise_again=False):
    """
    Sends a Message using Markdown as default.
    """
    bot = Bot(token=settings.TELEGRAM_BOT_KEY)
    try:
        return bot.send_message(chat_id=chat_id, text=msg, parse_mode=parse_mode, disable_web_page_preview=True)
    except ChatMigrated as e:
        notifications_logger.info(f"Chat migrated from chat_id={chat_id} to chat_id={e.new_chat_id}")
        if raise_again:
            raise e
    except BadRequest as e:  # Not enough rights to send text messages
        notifications_logger.exception(f"Not enough rights to send text messages chat_id={chat_id}")
        if raise_again:
            raise e
    except Unauthorized as e:
        notifications_logger.exception(f"Unauthorized to send message in chat_id={chat_id} msg={msg}\n{e}")
        if raise_again:
            raise e
    except TelegramError as e:
        notifications_logger.exception(f"Error Sending Message in Chat chat_id={chat_id} msg={msg}\n{e}")
        if raise_again:
            raise e
