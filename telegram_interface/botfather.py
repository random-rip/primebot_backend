from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext.filters import Filters

from data_crawling.api import Crawler
from parsing.regex_operations import TeamHTMLParser
from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Dispatcher, ConversationHandler

from telegram_interface.messages import START_GROUP, START_CHAT, HELP, OPTION1, OPTION1_AUSWAHL, OPTION2, \
    OPTION2_AUSWAHL, FINISH, ISSUE, \
    FEEDBACK

TEAM_ID, SETTING1, SETTING2, = range(3)


def start(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type == "group":
        update.message.reply_text(START_GROUP)
        return TEAM_ID
    else:
        update.message.reply_text(START_CHAT)
        return ConversationHandler.END


def get_team_id(update: Update, context: CallbackContext):
    link = update.message.text
    crawler = Crawler(local=False)
    team_id = link.split("/teams/")[-1].split("-")[0]
    team_parser = TeamHTMLParser(crawler.get_team_website(team_id))
    team_logo_url = team_parser.get_logo()
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
    update.message.reply_text(FINISH, markdown=True, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_text(HELP, markdown=True, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def issue(update: Update, context: CallbackContext):
    update.message.reply_text(ISSUE, markdown=True, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def feedback(update: Update, context: CallbackContext):
    update.message.reply_text(FEEDBACK, markdown=True, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        dp = updater.dispatcher
        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states={
                TEAM_ID: [MessageHandler(Filters.text, get_team_id),
                          CommandHandler('cancel', cancel),
                          ],

                SETTING1: [MessageHandler(Filters.text, setting1),
                           CommandHandler('cancel', cancel),
                           ],

                SETTING2: [MessageHandler(Filters.text, setting2),
                           CommandHandler('cancel', cancel),
                           ],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
            # CommandHandler("issue", issue),
            #
            # CommandHandler("feedback", feedback),
            # CommandHandler("help", helpcommand),

        )

        dp.add_handler(conv_handler)
        dp.add_handler(CommandHandler("help", helpcommand))
        dp.add_handler(CommandHandler("issue", issue))
        dp.add_handler(CommandHandler("feedback", feedback))
        updater.start_polling()
        updater.idle()
