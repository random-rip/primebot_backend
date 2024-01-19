from telegram import Chat, Message, Update

from bots.telegram_interface.commands.single_commands import call_match


class TestBot:
    response_text: str = ''

    def send_message(self, chat_id, *args, **kwargs):
        self.response_text = args[0] if args else kwargs.get("text", "")


class TestChat(Chat):
    type = Chat.CHANNEL


def test_call_match(text: str, chat, bot):
    message = Message(1, 1, None, chat, text=text, bot=bot)
    update = Update(1, message)

    call_match(update, None)
