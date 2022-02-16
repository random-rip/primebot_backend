import html
import logging

from bots.telegram_interface.tg_singleton import send_message_to_devs
from utils.utils import Encoder

logger = logging.getLogger("commands")


def create_log_message(prefix=None, separator="\n", **kwargs, ):
    """
    Anonymisiere ``user`` und ``chat_id`` und erstelle dann eine message.
    Args:
        prefix: Optional vorangestellter String
        separator: Join-Separator
        **kwargs: key,values which will be joined
    Returns: str

    """
    if "user" in kwargs:
        kwargs["user"] = Encoder.blake2b(kwargs["user"])
    if "chat_id" in kwargs:
        kwargs["chat_id"] = Encoder.blake2b(kwargs["chat_id"])

    text = ""
    if prefix:
        text += prefix
    text += separator.join([f"{key}: {value}" for key, value in kwargs.items()])
    return text


def log_command(fn):
    def wrapper(*args, **kwargs):
        update = args[0]
        command = fn.__name__
        result = fn(*args, **kwargs)

        params = {
            "chat_id": Encoder.blake2b(update.message.chat.id),
            "command": command,
            "message": update.message.text,
            "result": result,
        }
        if update.effective_user:
            params["user"] = update.effective_user.first_name

        message = create_log_message(prefix="TELEGRAM\n", **params)

        logger.info(message)
        send_message_to_devs(message)
        return result

    return wrapper


def log_callbacks(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].callback_query.message.chat.id
        command = fn.__name__
        message = args[0].callback_query.data
        question = args[0].callback_query.message.text.replace("\n", " ")
        result = fn(*args, **kwargs)

        params = {
            "chat_id": Encoder.blake2b(chat_id),
            "conversation": command,
            "question": question,
            "message": message,
            "result": result,
        }

        log_text = create_log_message(prefix="TELEGRAM\n", **params)
        logger.info(log_text)
        send_message_to_devs(log_text)
        return result

    return wrapper


async def log_from_discord(ctx, optional=None):
    author = ctx.message.author
    content = ctx.message.content

    params = {
        "user": author.name,
        "command": html.escape(str(content)),
        "server": html.escape(str(author.guild.name)),
        "server_members": author.guild.member_count,
    }

    if optional is not None:
        params["optional"] = html.escape(str(optional))

    log_text = create_log_message(prefix="DISCORD\n", **params)
    logger.info(log_text)
    send_message_to_devs(log_text)
    return True


def log_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            logging.getLogger("updates").exception(e)

    return wrapper
