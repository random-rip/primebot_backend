import logging
import sys
import traceback

from django.conf import settings
from telegram.error import ChatMigrated, TelegramError, Unauthorized
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Updater
from telegram.ext.filters import Filters

from bots import send_message
from bots.base.bot_interface import BotInterface
from bots.messages.base import BaseMessage
from bots.telegram_interface.commands import single_commands
from bots.telegram_interface.conversations import start_conversation
from bots.telegram_interface.tg_singleton import send_message_to_devs
from utils.exceptions import VariableNotSetException

notifications_logger = logging.getLogger("notifications")


class TelegramBot(BotInterface):
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    platform_name = "Telegram"

    def __init__(self):
        if not settings.TELEGRAM_BOT_KEY:
            raise VariableNotSetException("TELEGRAM_BOT_KEY")
        super().__init__(bot=Updater, bot_config={"token": settings.TELEGRAM_BOT_KEY, "use_context": True})

    def _initialize(self):
        dp = self.bot.dispatcher

        commands = [
            CommandHandler("cancel", single_commands.cancel),
            CommandHandler("help", single_commands.helpcommand),
            CommandHandler("bop", single_commands.bop),
            CommandHandler("setlogo", single_commands.set_logo),
            CommandHandler("match", single_commands.match),
            CommandHandler("matches", single_commands.matches),
            CommandHandler("delete", single_commands.delete),
            CommandHandler("settings", single_commands.team_settings),
            MessageHandler(Filters.status_update.migrate, single_commands.migrate_chat),  # Migration
        ]

        start_conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', start_conversation.start),
            ],
            states={
                1: [
                    MessageHandler(Filters.text & (~Filters.command), start_conversation.team_registration),
                ],
            },
            fallbacks=commands,
        )

        # Allgemeine Commands
        dp.add_handler(start_conv_handler)
        for cmd in commands[1:]:
            dp.add_handler(cmd)

        # Main Menu
        dp.add_handler(CallbackQueryHandler(start_conversation.finish_registration, pattern='0no'))
        dp.add_handler(CallbackQueryHandler(start_conversation.set_optional_photo, pattern='0yes'))
        # Chat Migration

        dp.add_error_handler(error)

    def run(self):
        self.bot.start_polling()  # TODO: try catch connection errors
        self.bot.idle()

    @staticmethod
    def send_message(*, msg: BaseMessage):
        """
        This method is designed to send non-interactive messages. This is usually triggered by prime league updates.
        To send a message from a user triggered action (f.e. a reply message), use context based messages
        directly. This is different for each of the communication platforms.
        """
        msg_content = msg.generate_message()
        try:
            send_message(msg=msg_content, chat_id=msg.team.telegram_id, raise_again=True)
        except ChatMigrated as e:
            msg.team.telegram_id = e.new_chat_id
            msg.team.save()
            send_message(msg=msg_content, chat_id=msg.team.telegram_id)
        except Unauthorized as e:
            notifications_logger.error(
                f"Unauthorized to send message in chat_id={msg.team.telegram_id}. Setting telegram_id to None.",
                e.message,
            )
            msg.team.set_telegram_null()
        except TelegramError as e:
            notifications_logger.error(f"Could not send Telegram Message {msg.__class__.__name__} to {msg.team}.", e)
            raise e


def error(update, context):
    try:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        notifications_logger.exception(trace)
        send_message_to_devs(
            msg=f"The error <code>{context.error}</code> happened in one of the telegram chats.", code=trace
        )

        if update and update.effective_message:
            text = (
                "Hey, es ist ein unerwarteter Fehler aufgetreten, während ich euren Befehl verarbeiten wollte. "
                "Bitte kontaktiert die Programmierer über Discord oder Telegram."
            )
            update.effective_message.reply_text(text)
    except Exception as e:
        text = "Ein gravierender Fehler ist aufgetreten."
        send_message_to_devs(text, code=str(e))
    try:
        raise
    except RuntimeError:
        pass
