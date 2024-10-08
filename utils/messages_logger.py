import html
import logging

from discord import Interaction
from django.conf import settings

from bots.telegram_interface.tg_singleton import send_message_to_devs
from utils.utils import Encoder

logger = logging.getLogger("commands")


def create_log_message(prefix=None, separator="\n", **kwargs):
    """
    Anonymisiere ``user``, `channel` und ``chat_id`` und erstelle dann eine message.
    Args:
        prefix: Optional vorangestellter String
        separator: Join-Separator
        **kwargs: key,values which will be joined
    Returns: str

    """
    if "user" in kwargs:
        kwargs["user"] = Encoder.blake2b(kwargs["user"])
    if "channel" in kwargs:
        kwargs["channel"] = Encoder.blake2b(kwargs["channel"])
    if "chat_id" in kwargs:
        kwargs["chat_id"] = Encoder.blake2b(kwargs["chat_id"])

    text = ""
    if prefix:
        text += prefix
    text += separator.join([f"{key}: {value}" for key, value in kwargs.items()])
    return text


def log_command(fn):
    def wrapper(*args, **kwargs):
        result = fn(*args, **kwargs)
        if settings.DEBUG:
            return result
        update = args[0]
        command = fn.__name__
        params = {
            "chat_id": Encoder.blake2b(update.message.chat.id),
            "command": command,
            "message": update.message.text,
            "result": result,
        }
        if update.effective_user:
            params["user"] = update.effective_user.first_name

        log_text = create_log_message(prefix="TELEGRAM\n", **params)

        spread_message(log_text)
        return result

    return wrapper


def log_callbacks(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].callback_query.message.chat.id
        command = fn.__name__
        message = args[0].callback_query.data
        question = args[0].callback_query.message.text.replace("\n", " ")
        result = fn(*args, **kwargs)
        if settings.DEBUG:
            return result

        params = {
            "chat_id": Encoder.blake2b(chat_id),
            "conversation": command,
            "question": question,
            "message": message,
            "result": result,
        }

        log_text = create_log_message(prefix="TELEGRAM\n", **params)
        spread_message(log_text)
        return result

    return wrapper


async def log_from_discord(interaction: Interaction, optional=None):
    author = interaction.user
    params = {
        "user": author.name,
        "user_locale": html.escape(str(interaction.locale)),
        "command": html.escape(str(interaction.command.name)),
        "channel": html.escape(str(interaction.channel_id)),
        "channel_type": html.escape(str(interaction.channel.type.name)),
    }
    if "options" in interaction.data:
        readable_parameters = [f"{x['name']}: {html.escape(str(x['value']))}" for x in interaction.data["options"]]
        params["parameters"] = str(readable_parameters)

    if hasattr(author, "guild"):
        params["server"] = html.escape(str(author.guild.name))
        params["members"] = author.guild.member_count
        params["preferred_guild_locale"] = author.guild.preferred_locale

    if optional is not None:
        params["optional"] = html.escape(str(optional))

    log_text = create_log_message(prefix="DISCORD\n", **params)
    spread_message(log_text)


def log_exception(fn):
    def wrapper(*args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
            logging.getLogger("updates").exception(e)
            # text = f"Error in Updates: <code>{e}</code>\n. See <code>update.log</code> for more information."
            # send_message_to_devs(text) # TODO Nur einen Log senden und nicht 1000 alle 15 Minuten"

    return wrapper


def spread_message(log_text: str):
    logger.info(log_text.replace("\n", ";"))
    send_message_to_devs(log_text)
