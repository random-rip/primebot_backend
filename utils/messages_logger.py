import html
import logging

from django.conf import settings
from telegram import ParseMode
from telegram.utils.helpers import mention_html

from communication_interfaces.telegram_interface.tg_singleton import send_message

logger = logging.getLogger("commands")


def log_command(fn):
    def wrapper(*args, **kwargs):
        update = args[0]
        command = fn.__name__
        result = fn(*args, **kwargs)

        user = f'{mention_html(update.effective_user.id, update.effective_user.first_name)}' if update.effective_user else ""

        title = update.effective_chat.title if update.effective_chat else ""

        log_text = (
            f"Chat: {update.message.chat.id} (Title <i>{title}</i>) (User {user}), "
            f"Command: {command}, "
            f"Message: {update.message.text}, "
            f"Result-Code: {result}"
        )

        logger.info(log_text)
        try:
            send_command_to_dev_group(log_text)
        except Exception as e:
            logger.error(e)
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
            f"Chat: {chat_id}, "
            f"Conversation: {command}, "
            f"Question: '{question}', "
            f"Message: '{message}', "
            f"Result-Code: {result}"
        )
        logger.info(log_text)
        try:
            send_command_to_dev_group(log_text)
        except Exception as e:
            logger.error(e)
        return result

    return wrapper


def send_command_to_dev_group(log, parse_mode=ParseMode.HTML):
    send_message(msg=log, chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=parse_mode)


async def log_from_discord(ctx, optional=None):
    channel = ctx.message.channel
    author = ctx.message.author
    content = ctx.message.content
    log_text = (
        f"DISCORD Channel: <i>{html.escape(str(channel.name))}</i> "
        f"(User={html.escape(str(author.name))}#{author.discriminator}), "
        f"CommandMessage=<code>{html.escape(str(content))}</code>, "
        f"Servername=<i>{html.escape(str(author.guild.name))}</i>: {author.guild.member_count} Members."
    )
    if optional is not None:
        log_text = f"{log_text}\n===\nOPTIONAL_RESULT: <code>{html.escape(str(optional))}</code>"
    try:
        logger.info(log_text)
        send_command_to_dev_group(log_text)
    except Exception as e:
        logger.error(e)
    finally:
        return True


def log_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            logging.getLogger("django").error(e)
    return wrapper
