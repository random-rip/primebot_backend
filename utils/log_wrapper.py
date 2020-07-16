import logging
import os

from prime_league_bot.settings import LOGGING_DIR

logging.basicConfig(
    filename=os.path.join(LOGGING_DIR, "bot_father.log"),
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
logger = logging.getLogger()


def log_command(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].message.chat.id
        command = fn.__name__
        message = args[0].message.text
        result = fn(*args, **kwargs)
        logger.info(f"Chat: {chat_id}, Command: {command}, Message: {message}, Result-Code: {result}")
        return result

    return wrapper
