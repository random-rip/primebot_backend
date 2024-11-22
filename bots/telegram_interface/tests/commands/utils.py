from datetime import datetime
from unittest.mock import MagicMock

from telegram import Chat, Message, Update

from bots.telegram_interface.commands.single_commands import call_match


class BotMock(MagicMock):
    response_text: str = ''

    def send_message(self, chat_id, *args, **kwargs):
        self.response_text = args[0] if args else kwargs.get("text", "")


class TestChat(Chat):
    type = Chat.CHANNEL


def test_call_match(text: str, chat=None, bot=None):
    chat = chat or Chat(1, Chat.CHANNEL)
    bot = bot or BotMock()
    message = Message(1, chat=chat, text=text, bot=bot, date=datetime.now())
    update = Update(1, message)
    call_match(update, MagicMock())
