import logging

from telegram_interface.tg_singleton import TelegramMessagesWrapper

logger = logging.getLogger("commands_logger")


def log_command(fn):
    def wrapper(*args, **kwargs):
        chat_id = args[0].message.chat.id
        command = fn.__name__
        message = args[0].message.text
        result = fn(*args, **kwargs)
        log_text = (f"Chat: {chat_id}, "
                    f"Command: {command}, "
                    f"Message: {message}, "
                    f"Result-Code: {result}")
        logger.info(log_text)
        try:
            TelegramMessagesWrapper.send_command(log_text)
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
            TelegramMessagesWrapper.send_command(log_text)
        except Exception as e:
            logger.error(e)
        return result

    return wrapper
