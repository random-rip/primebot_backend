from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, \
    CallbackQueryHandler
from telegram.ext.filters import Filters

from prime_league_bot import settings
from telegram_interface.commands.single_commands import cancel, helpcommand, issue, feedback, bop, explain
from telegram_interface.conversations.settings_conversation import main_settings_menu, callback_query_settings_handlers, \
    start_settings
from telegram_interface.conversations.start_conversation import start, get_team_id


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        dp = updater.dispatcher

        fallbacks = [
            CommandHandler("cancel", cancel),
            CommandHandler("help", helpcommand),
            CommandHandler("issue", issue),
            CommandHandler("feedback", feedback),
            CommandHandler("bop", bop),
            CommandHandler("explain", explain),
        ]

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states={
                1: [MessageHandler(Filters.text & (~Filters.command), get_team_id), ],
            },

            fallbacks=fallbacks
        )

        # Allgemeine Commands
        dp.add_handler(conv_handler)
        for cmd in fallbacks[1:]:
            dp.add_handler(cmd)

        # Main Menu
        dp.add_handler(CommandHandler('settings', start_settings))
        dp.add_handler(CallbackQueryHandler(main_settings_menu, pattern='main'))

        for i in callback_query_settings_handlers:
            dp.add_handler(i)

        updater.start_polling()
        updater.idle()
