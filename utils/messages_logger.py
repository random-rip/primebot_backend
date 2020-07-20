import logging
import os
from datetime import datetime

from prime_league_bot.settings import LOGGING_DIR

logging.basicConfig(
    filename=os.path.join(LOGGING_DIR, f"messages_{datetime.now().strftime('%Y-%m-%d')}.log"),
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


def log_conversation(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].callback_query.message.chat.id
        command = fn.__name__
        message = args[0].callback_query.data
        question = args[0].callback_query.message.text.replace("\n", " ")
        result = fn(*args, **kwargs)
        logger.info(
            f"Chat: {chat_id}, "
            f"Conversation: {command}, "
            f"Question: '{question}', "
            f"Message: '{message}', "
            f"Result-Code: {result}"
        )
        return result

    return wrapper
