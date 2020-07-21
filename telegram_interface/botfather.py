from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, \
    CallbackQueryHandler
from telegram.ext.filters import Filters

from prime_league_bot import settings
from telegram_interface.commands.single_commands import cancel, helpcommand, issue, feedback, bop, explain, set_logo
from telegram_interface.conversations.settings_conversation import main_settings_menu, callback_query_settings_handlers, \
    start_settings, main_settings_menu_close, migrate_chat
from telegram_interface.conversations.start_conversation import start, team_registration, finish_registration, \
    set_optional_photo


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

        # liveticker_conv_handler = ConversationHandler(
        #     entry_points=[CallbackQueryHandler(main_settings_menu, pattern='main', )],
        #
        #     states={
        #         1: [MessageHandler(Filters.text & (~Filters.command), liveticker_add_team), ],
        #     },
        #
        #     fallbacks=fallbacks,
        # )

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
        for i in callback_query_settings_handlers:
            dp.add_handler(i)
        updater.start_polling()
        updater.idle()
