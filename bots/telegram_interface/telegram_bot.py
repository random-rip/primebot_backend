import logging
import sys
import traceback

import telepot
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.utils.helpers import mention_html
from telepot.exception import BotWasKickedError, BotWasBlockedError

from bots import send_message
from bots.base.bot import Bot
from bots.languages.de_DE import MESSAGE_NOT_PINNED_TEXT, CANT_PIN_MSG_IN_PRIVATE_CHAT
from bots.messages import BaseMessage
from bots.telegram_interface.commands import single_commands
from bots.telegram_interface.conversations import start_conversation
from bots.telegram_interface.tg_singleton import pin_msg, CannotBePinnedError
from prime_league_bot import settings


class TelegramBot(Bot):
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        super().__init__(
            bot=Updater,
            bot_config={
                "token": settings.TELEGRAM_BOT_KEY,
                "use_context": True
            }
        )

    def _initialize(self):
        dp = self.bot.dispatcher

        commands = [
            CommandHandler("cancel", single_commands.cancel),
            CommandHandler("help", single_commands.helpcommand),
            CommandHandler("issue", single_commands.issue),
            CommandHandler("feedback", single_commands.feedback),
            CommandHandler("bop", single_commands.bop),
            CommandHandler("explain", single_commands.explain),
            CommandHandler("setlogo", single_commands.set_logo),
            CommandHandler("overview", single_commands.overview),
            CommandHandler("delete", single_commands.delete),
            CommandHandler("settings", single_commands.team_settings),
            MessageHandler(Filters.status_update.migrate, single_commands.migrate_chat)  # Migration
        ]

        start_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start_conversation.start, )],

            states={
                1: [MessageHandler(Filters.text & (~Filters.command), start_conversation.team_registration), ],
            },

            fallbacks=commands
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
    def send_message(*, msg: BaseMessage, team):
        try:
            sent_message = send_message(msg=msg.message, chat_id=team.telegram_id, raise_again=True)
        except (BotWasKickedError, BotWasBlockedError) as e:
            team.set_telegram_null()
            logging.getLogger("notifications").info(f"Soft deleted Telegram {team}'")
            return
        except Exception as e:
            print(e)
            return
        if msg.can_be_pinned():
            try:
                pin_msg(sent_message)
            except CannotBePinnedError:
                send_message(msg=MESSAGE_NOT_PINNED_TEXT, chat_id=team.telegram_id)
            except telepot.exception.TelegramError:
                logging.getLogger("notifications").exception(f"{team}: {CANT_PIN_MSG_IN_PRIVATE_CHAT}")
        return


def error(update, context):
    try:
        if update is not None:
            if update.effective_message:
                text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your request. " \
                       "My developer(s) will be notified."
                update.effective_message.reply_text(text)
            trace = "".join(traceback.format_tb(sys.exc_info()[2]))
            payload = ""
            if update.effective_user:
                payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
            if update.effective_chat:
                payload += f' within the chat <i>{update.effective_chat.title}</i>'
                if update.effective_chat.username:
                    payload += f' (@{update.effective_chat.username})'
            if update.poll:
                payload += f' with the poll id {update.poll.id}.'
            text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
                   f"</code>"
        else:
            text = "Ein Fehler ist aufgetreten (update is none)."
        context.bot.send_message(settings.TG_DEVELOPER_GROUP, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        text = f"Ein gravierender Fehler ist aufgetreten.\n{e}"
        # TODO: catch connection errors
        context.bot.send_message(settings.TG_DEVELOPER_GROUP, text, parse_mode=ParseMode.HTML)
    try:
        raise
    except RuntimeError as e:
        logging.getLogger("django").exception(e)
