from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext.filters import Filters

from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Dispatcher, ConversationHandler

from telegram_interface.messages import START, HELP, OPTION1, OPTION1_AUSWAHL, OPTION2, OPTION2_AUSWAHL, FINISH, ISSUE, \
    FEEDBACK

TEAM_ID, SETTING1, SETTING2, = range(3)


def start(update: Update, context: CallbackContext):
    update.message.reply_text(START)
    return TEAM_ID


def get_team_id(update: Update, context: CallbackContext):
    link = update.message.text
    team_id = link.split("/teams/")[-1].split("-")[0]
    print(team_id)
    reply_keyboard = [OPTION1_AUSWAHL]
    update.message.reply_text(
        OPTION1,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        markdown=True
    )
    return SETTING1


def setting1(update: Update, context: CallbackContext):
    reply_keyboard = [OPTION2_AUSWAHL]
    update.message.reply_text(
        OPTION2,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        markdown=True
    )

    return SETTING2


def setting2(update: Update, context: CallbackContext):
    update.message.reply_text(FINISH, markdown=True)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_text(HELP, markdown=True)


def issue(update: Update, context: CallbackContext):
    update.message.reply_text(ISSUE, markdown=True)


def feedback(update: Update, context: CallbackContext):
    update.message.reply_text(FEEDBACK, markdown=True)


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True)
        dp = updater.dispatcher
        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],

            states={
                TEAM_ID: [MessageHandler(Filters.text, get_team_id)],

                SETTING1: [MessageHandler(Filters.text, setting1)],

                SETTING2: [MessageHandler(Filters.text, setting2)],

            },

            fallbacks=[CommandHandler('cancel', cancel)]

        )

        dp.add_handler(conv_handler)
        dp.add_handler(CommandHandler("help", helpcommand))
        dp.add_handler(CommandHandler("issue", issue))
        dp.add_handler(CommandHandler("feedback", feedback))
        updater.start_polling()
        updater.idle()
