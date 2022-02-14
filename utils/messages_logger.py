import html
import logging

from bots.telegram_interface.tg_singleton import send_message_to_devs
from utils.utils import Encoder

logger = logging.getLogger("commands")


def log_command(fn):
    def wrapper(*args, **kwargs):
        update = args[0]
        command = fn.__name__
        result = fn(*args, **kwargs)

        user = update.effective_user.first_name if update.effective_user else ""
        user = Encoder.blake2b(user)

        chat_id = Encoder.blake2b(update.message.chat.id)
        log_text = (
            f"Chat: {chat_id}, "
            f"User: {user}, "
            f"Command: {command}, "
            f"Message: {update.message.text}, "
            f"Result-Code: {result}"
        )

        logger.info(log_text)
        send_message_to_devs(log_text)
        return result

    return wrapper


def log_callbacks(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].callback_query.message.chat.id
        command = fn.__name__
        message = args[0].callback_query.data
        question = args[0].callback_query.message.text.replace("\n", " ")
        result = fn(*args, **kwargs)
        log_text = (
            f"Chat: {Encoder.blake2b(chat_id)}, "
            f"Conversation: {command}, "
            f"Question: '{question}', "
            f"Message: '{message}', "
            f"Result-Code: {result}"
        )
        logger.info(log_text)
        send_message_to_devs(log_text)
        return result

    return wrapper


async def log_from_discord(ctx, optional=None):
    author = ctx.message.author
    content = ctx.message.content
    log_text = (
        f"DISCORD\n"
        f"User: {Encoder.blake2b(author.name)}"
        f"CommandMessage: <code>{html.escape(str(content))}</code>, "
        f"Server: <i>{html.escape(str(author.guild.name))}</i>: {author.guild.member_count} Members."
    )
    if optional is not None:
        log_text = f"{log_text} OPTIONAL_RESULT: <code>{html.escape(str(optional))}</code>"
    logger.info(log_text)
    send_message_to_devs(log_text)
    return True


def log_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            logging.getLogger("django").exception(e)

    return wrapper
