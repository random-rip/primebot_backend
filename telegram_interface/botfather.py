from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext.filters import Filters
import requests

from app_prime_league.teams import register_team
from data_crawling.api import Crawler
from parsing.parser import TeamHTMLParser
from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Dispatcher, ConversationHandler

from telegram_interface.messages import START_GROUP, START_CHAT, HELP, OPTION1, OPTION1_AUSWAHL, OPTION2, \
    OPTION2_AUSWAHL, FINISH, ISSUE, \
    FEEDBACK, START_SETTINGS, OPTION3, OPTION3_AUSWAHL

TEAM_ID, SETTING1, SETTING2, SETTING3 = range(4)


def start(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type == "group":
        update.message.reply_text(START_GROUP)
        return TEAM_ID
    else:
        update.message.reply_text(START_CHAT)
        return ConversationHandler.END


def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    chat_id = update.message.chat_id
    bot = context.bot
    bot.send_photo(chat_id=chat_id, photo=url)


def get_team_id(update: Update, context: CallbackContext):
    link = update.message.text
    team_id = link.split("/teams/")[-1].split("-")[0]
    tg_group_id = update["message"]["chat"]["id"]
    register_team(team_id=team_id, tg_group_id=tg_group_id)
    reply_keyboard = OPTION1_AUSWAHL
    update.message.reply_text(
        "Erkannte TeamID: " + team_id + "\n" + OPTION1,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        markdown=True,
        resize_keyboard=True,
    )
    return SETTING1


def setting1(update: Update, context: CallbackContext):
    reply_keyboard = OPTION2_AUSWAHL
    settings_dict = {
        ""
    }
    update.message.reply_text(
        OPTION2,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        markdown=True
    )
    return SETTING2


def setting2(update: Update, context: CallbackContext):
    reply_keyboard = OPTION3_AUSWAHL
    update.message.reply_text(
        OPTION3,
        markdown=True,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return SETTING3


def setting3(update: Update, context: CallbackContext):
    update.message.reply_text(
        FINISH,
        markdown=True,
        reply_markup=ReplyKeyboardRemove()
    )
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


def start_settings(update: Update, context: CallbackContext):
    reply_keyboard = OPTION1_AUSWAHL
    update.message.reply_text(
        START_SETTINGS + "\n" + OPTION1,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        markdown=True
    )
    return SETTING1


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        dp = updater.dispatcher
        # Add conversation handler with the states TEAM_ID, SETTING1, SETTING2
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states={
                TEAM_ID: [MessageHandler(Filters.text & (~Filters.command), get_team_id), ],

                SETTING1: [MessageHandler(Filters.text & (~Filters.command), setting1), ],

                SETTING2: [MessageHandler(Filters.text & (~Filters.command), setting2), ],

                SETTING3: [MessageHandler(Filters.text & (~Filters.command), setting3), ],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )
        conv_handler_settings = ConversationHandler(
            entry_points=[CommandHandler('settings', start_settings, )],

            states={
                SETTING1: [MessageHandler(Filters.text & (~Filters.command), setting1), ],

                SETTING2: [MessageHandler(Filters.text & (~Filters.command), setting2), ],

                SETTING3: [MessageHandler(Filters.text & (~Filters.command), setting3), ],

            },

            fallbacks=[CommandHandler('cancel', cancel)]
        )

        dp.add_handler(conv_handler)
        dp.add_handler(conv_handler_settings)
        dp.add_handler(CommandHandler("help", helpcommand))
        dp.add_handler(CommandHandler("issue", issue))
        dp.add_handler(CommandHandler("feedback", feedback))
        dp.add_handler(CommandHandler("bop", bop))
        updater.start_polling()
        updater.idle()
