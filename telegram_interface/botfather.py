import sys
import traceback

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, \
    CallbackQueryHandler
from telegram.ext.filters import Filters
from telegram.utils.helpers import mention_html

from prime_league_bot import settings
from telegram_interface.commands.single_commands import cancel, helpcommand, issue, feedback, bop, explain, set_logo
from telegram_interface.conversations.settings_conversation import main_settings_menu, callback_query_settings_handlers, \
    start_settings, main_settings_menu_close, migrate_chat
from telegram_interface.conversations.start_conversation import start, team_registration, finish_registration, \
    set_optional_photo


# this is a general error handler function. If you need more information about specific type of update, add it to the
# payload in the respective if clause
def error(update, context):
    # add all the dev user_ids in this list. You can also add ids of channels or groups.
    devs = [-490819576]
    # we want to notify the user of this problem. This will always work, but not notify users if the update is an
    # callback or inline query, or a poll update. In case you want this, keep in mind that sending the message
    # could fail
    try:
        if update is not None:
            if update.effective_message:
                text = "Hey. I'm sorry to inform you that an error happened while I tried to handle your update. " \
                       "My developer(s) will be notified."
                update.effective_message.reply_text(text)
            # This traceback is created with accessing the traceback object from the sys.exc_info, which is returned as the
            # third value of the returned tuple. Then we use the traceback.format_tb to get the traceback as a string, which
            # for a weird reason separates the line breaks in a list, but keeps the linebreaks itself. So just joining an
            # empty string works fine.
            trace = "".join(traceback.format_tb(sys.exc_info()[2]))
            # lets try to get as much information from the telegram update as possible
            payload = ""
            # normally, we always have an user. If not, its either a channel or a poll update.
            if update.effective_user:
                payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
            # there are more situations when you don't get a chat
            if update.effective_chat:
                payload += f' within the chat <i>{update.effective_chat.title}</i>'
                if update.effective_chat.username:
                    payload += f' (@{update.effective_chat.username})'
            # but only one where you have an empty payload by now: A poll (buuuh)
            if update.poll:
                payload += f' with the poll id {update.poll.id}.'
            # lets put this in a "well" formatted text
            text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
                   f"</code>"
            # and send it to the dev(s)
        else:
            text = "Ein gravierender Fehler ist aufgetreten (update is none)."
    except Exception as e:
        text = f"Ein gravierender Fehler ist aufgetreten.\n{e}"
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    # we raise the error again, so the logger module catches it. If you don't use the logger module, use it.
    raise


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(self.api_key, use_context=True, )
        dp = updater.dispatcher

        fallbacks = [
            CommandHandler("cancel", cancel),
            CommandHandler("help", helpcommand),
            CommandHandler("issue", issue),
            CommandHandler("feedback", feedback),
            CommandHandler("bop", bop),
            CommandHandler("explain", explain),
            CommandHandler("setlogo", set_logo),
        ]

        start_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states={
                1: [MessageHandler(Filters.text & (~Filters.command), team_registration), ],
            },

            fallbacks=fallbacks
        )

        # Allgemeine Commands
        dp.add_handler(start_conv_handler)
        for cmd in fallbacks[1:]:
            dp.add_handler(cmd)

        # Main Menu
        dp.add_handler(CommandHandler('settings', start_settings))
        dp.add_handler(CallbackQueryHandler(main_settings_menu, pattern='main'))
        dp.add_handler(CallbackQueryHandler(main_settings_menu_close, pattern='close'))
        dp.add_handler(CallbackQueryHandler(finish_registration, pattern='0no'))
        dp.add_handler(CallbackQueryHandler(set_optional_photo, pattern='0yes'))
        # Chat Migration
        dp.add_handler(MessageHandler(Filters.status_update.migrate, migrate_chat))

        dp.add_error_handler(error)

        for i in callback_query_settings_handlers:
            dp.add_handler(i)
        updater.start_polling()
        updater.idle()
