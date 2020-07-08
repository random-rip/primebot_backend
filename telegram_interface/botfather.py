from itertools import chain

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext.filters import Filters
import requests

from app_prime_league.teams import register_team, update_team
from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Dispatcher, ConversationHandler

from telegram_interface.messages import START_GROUP, START_CHAT, HELP, FINISH, ISSUE, \
    FEEDBACK, START_SETTINGS, BOOLEAN_KEYBOARD, TEAM_EXISTING, SETTINGS

TEAM_ID, SETTING1, SETTING2, SETTING3, SETTING4 = range(5)

boolean_keyboard = ["Ja", "Nein"]


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
    team = register_team(team_id=team_id, tg_group_id=tg_group_id)
    if team is None:
        update.message.reply_text(TEAM_EXISTING)
        return TEAM_ID
    else:
        update.message.reply_text(
            "Erkannte TeamID: " + team_id + "\n" + SETTINGS[0]["text"],
            reply_markup=ReplyKeyboardMarkup(SETTINGS[0]["keyboard"], one_time_keyboard=True),
            markdown=True,
        )
        return SETTING1


def weekly_op_link(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[0]["keyboard"])):
        update.message.reply_text(
            SETTINGS[0]["text"],
            markdown=True,
            reply_markup=ReplyKeyboardMarkup(SETTINGS[0]["keyboard"], one_time_keyboard=True)
        )
        return SETTING1

    settings = {
        "weekly_op_link": True if answer == "Ja" else False,
    }
    tg_chat_id = update["message"]["chat"]["id"]
    update_team(tg_chat_id, settings=settings)
    update.message.reply_text(
        SETTINGS[1]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[1]["keyboard"], one_time_keyboard=True),
        markdown=True
    )
    return SETTING2


def lineup_op_link(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[1]["keyboard"])):
        update.message.reply_text(
            SETTINGS[1]["text"],
            markdown=True,
            reply_markup=ReplyKeyboardMarkup(SETTINGS[1]["keyboard"], one_time_keyboard=True)
        )
        return SETTING2

    settings = {
        "lineup_op_link": True if answer == "Ja" else False,
    }
    tg_chat_id = update["message"]["chat"]["id"]
    update_team(tg_chat_id, settings=settings)
    update.message.reply_text(
        SETTINGS[2]["text"],
        markdown=True,
        reply_markup=ReplyKeyboardMarkup(SETTINGS[2]["keyboard"], one_time_keyboard=True)
    )
    return SETTING3


def scheduling_suggestion(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[2]["keyboard"])):
        update.message.reply_text(
            SETTINGS[2]["text"],
            markdown=True,
            reply_markup=ReplyKeyboardMarkup(SETTINGS[2]["keyboard"], one_time_keyboard=True)
        )
        return SETTING3
    settings = {
        "scheduling_suggestion": True if answer == "Ja" else False,
    }
    tg_chat_id = update["message"]["chat"]["id"]
    update_team(tg_chat_id, settings=settings)
    update.message.reply_text(
        SETTINGS[3]["text"],
        markdown=True,
        reply_markup=ReplyKeyboardMarkup(SETTINGS[3]["keyboard"], one_time_keyboard=True)
    )
    return SETTING4


def scheduling_confirmation(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[3]["keyboard"])):
        update.message.reply_text(
            SETTINGS[3]["text"],
            markdown=True,
            reply_markup=ReplyKeyboardMarkup(SETTINGS[3]["keyboard"], one_time_keyboard=True)
        )
        return SETTING4
    settings = {
        "scheduling_confirmation": True if answer == "Ja" else False,
    }
    tg_chat_id = update["message"]["chat"]["id"]
    update_team(tg_chat_id, settings=settings)
    update.message.reply_text(
        FINISH,
        markdown=True,
        reply_markup=ReplyKeyboardRemove(),
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
    update.message.reply_text(
        START_SETTINGS + "\n" + SETTINGS[TEAM_ID]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[TEAM_ID]["keyboard"], one_time_keyboard=True),
        markdown=True
    )
    return SETTING1


def setting(update: Update, context: CallbackContext, num):
    print("test")


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        dp = updater.dispatcher
        states = {}
        # for i, set in enumerate(SETTINGS):
        #     states.update({i: [MessageHandler(Filters.text & (~Filters.command), setting(num=i))]})

        states = {
            TEAM_ID: [MessageHandler(Filters.text & (~Filters.command), get_team_id), ],

            SETTING1: [MessageHandler(Filters.text & (~Filters.command), weekly_op_link), ],

            SETTING2: [MessageHandler(Filters.text & (~Filters.command), lineup_op_link), ],

            SETTING3: [MessageHandler(Filters.text & (~Filters.command), scheduling_suggestion), ],

            SETTING4: [MessageHandler(Filters.text & (~Filters.command), scheduling_confirmation), ],

        }
        # Add conversation handler with the states TEAM_ID, SETTING1, SETTING2
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states=states,

            fallbacks=[CommandHandler('cancel', cancel)]
        )
        conv_handler_settings = ConversationHandler(
            entry_points=[CommandHandler('settings', start_settings, )],

            states=states,

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
