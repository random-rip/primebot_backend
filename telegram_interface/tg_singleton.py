import telepot

from prime_league_bot import settings

bot = telepot.Bot(token=settings.TELEGRAM_BOT_KEY)


def send_message(msg: str, chat_id: int = None):
    """
    Sends a Message using Markdown. If settings.DEBUG is True, overwrites the chat_id.
    """
    if settings.DEBUG or chat_id is None:
        chat_id = settings.DEFAULT_TELEGRAM_CHANNEL_ID
    bot.sendMessage(chat_id=chat_id, text=msg, parse_mode="Markdown")
