from telegram.ext import Updater, CommandHandler

from prime_league_bot import settings


class LiveTicker:

    def __init__(self):
        self.api_key = settings.TELEGRAM_LIVETICKER_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        dp = updater.dispatcher

        fallbacks = [
            # CommandHandler("cancel", cancel),
            # CommandHandler("help", helpcommand),
            # CommandHandler("issue", issue),
            # CommandHandler("feedback", feedback),
            # CommandHandler("bop", bop),
            # CommandHandler("explain", explain),
            # CommandHandler("setlogo", set_logo),
        ]

        for cmd in fallbacks[1:]:
            dp.add_handler(cmd)
        updater.start_polling()
        updater.idle()
