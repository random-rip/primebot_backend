import os
import urllib.request
from itertools import chain

from django.core.files import File
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext.filters import Filters
import requests

from app_prime_league.teams import register_team, update_team
from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ConversationHandler

from prime_league_bot.settings import LOGGING_DIR
from telegram_interface.messages import START_GROUP, START_CHAT, HELP_COMMAND_LIST, SETTINGS_FINISHED, ISSUE, \
    FEEDBACK, START_SETTINGS, TEAM_EXISTING, SETTINGS, CANCEL, SKIP, YES, TEAM_ID_VALID, HELP_TEXT, REGISTRATION_FINISH, \
    WAIT_A_MOMENT_TEXT, EXPLAIN_TEXT, NO_GROUP_CHAT, TEAM_NOT_IN_DB_TEXT, TEAM_ID_NOT_VALID_TEXT
from telegram_interface.tg_singleton import TelegramMessagesWrapper
from utils.log_wrapper import log_command
from utils.utils import current_game_day

TEAM_ID, SETTING1, SETTING2, SETTING3, SETTING4 = range(5)


@log_command
def start(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type == "group":
        update.message.reply_markdown(START_GROUP, disable_web_page_preview=True)
        return TEAM_ID
    else:
        update.message.reply_markdown(START_CHAT, parse_mode="Markdown", disable_web_page_preview=True)
        return ConversationHandler.END


def set_photo(update: Update, context: CallbackContext, url):
    chat_id = update.message.chat_id
    file_name = f"temp_{chat_id}.temp"
    _ = urllib.request.urlretrieve(url, file_name)

    try:
        with open(file_name, 'rb') as f:
            context.bot.set_chat_photo(
                chat_id=chat_id,
                photo=File(f),
                timeout=20,
            )
        os.remove(file_name)
    except FileNotFoundError as e:
        return "File nicht gefunden"


def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    set_photo(update, context, url)
    chat_id = update.message.chat_id
    bot = context.bot
    bot.send_photo(chat_id=chat_id, photo=url)


@log_command
def get_team_id(update: Update, context: CallbackContext):
    response = update.message.text
    try:
        team_id = int(response)
    except Exception as e:
        try:
            team_id = int(response.split("/teams/")[-1].split("-")[0])
        except Exception as e:
            update.message.reply_markdown(
                TEAM_ID_NOT_VALID_TEXT,
            )
            return TEAM_ID

    tg_group_id = update["message"]["chat"]["id"]
    context.bot.send_message(
        text=WAIT_A_MOMENT_TEXT,
        chat_id=tg_group_id,
        parse_mode="Markdown",
    )
    team = register_team(team_id=team_id, tg_group_id=tg_group_id)
    if team is None:
        update.message.reply_markdown(
            TEAM_EXISTING,
            disable_web_page_preview=True,
        )
        return TEAM_ID
    else:
        update.message.reply_markdown(
            f"{TEAM_ID_VALID}*{team.name}*\n{REGISTRATION_FINISH}",
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True,
        )
        next_game = team.games_against.filter(game_day=current_game_day()).first()
        if next_game is not None:
            TelegramMessagesWrapper.send_next_game_day_after_registration(next_game)
        return ConversationHandler.END


@log_command
def weekly_op_link(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[0]["keyboard"])):
        update.message.reply_markdown(
            SETTINGS[0]["text"],
            reply_markup=ReplyKeyboardMarkup(SETTINGS[0]["keyboard"], one_time_keyboard=True),
            disable_web_page_preview=True,
        )
        return SETTING1

    settings = {
        SETTINGS[0]["name"]: True if answer == YES else False,
    }
    if answer != SKIP:
        tg_chat_id = update["message"]["chat"]["id"]
        team = update_team(tg_chat_id, settings=settings)
        if team is None:
            return team_not_exists(update, context)
    update.message.reply_markdown(
        SETTINGS[1]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[1]["keyboard"], one_time_keyboard=True),
        disable_web_page_preview=True,
    )
    return SETTING2


@log_command
def lineup_op_link(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[1]["keyboard"])):
        update.message.reply_markdown(
            SETTINGS[1]["text"],
            reply_markup=ReplyKeyboardMarkup(SETTINGS[1]["keyboard"], one_time_keyboard=True),
            disable_web_page_preview=True,
        )
        return SETTING2

    settings = {
        SETTINGS[1]["name"]: True if answer == YES else False,
    }
    if answer != SKIP:
        tg_chat_id = update["message"]["chat"]["id"]
        update_team(tg_chat_id, settings=settings)
    update.message.reply_markdown(
        SETTINGS[2]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[2]["keyboard"], one_time_keyboard=True),
        disable_web_page_preview=True,
    )
    return SETTING3


@log_command
def scheduling_suggestion(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[2]["keyboard"])):
        update.message.reply_markdown(
            SETTINGS[2]["text"],
            reply_markup=ReplyKeyboardMarkup(SETTINGS[2]["keyboard"], one_time_keyboard=True),
            disable_web_page_preview=True,
        )
        return SETTING3
    settings = {
        SETTINGS[2]["name"]: True if answer == YES else False,
    }
    if answer != SKIP:
        tg_chat_id = update["message"]["chat"]["id"]
        update_team(tg_chat_id, settings=settings)

    update.message.reply_markdown(
        SETTINGS[3]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[3]["keyboard"], one_time_keyboard=True),
        disable_web_page_preview=True,
    )
    return SETTING4


@log_command
def scheduling_confirmation(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer not in list(chain(*SETTINGS[3]["keyboard"])):
        update.message.reply_markdown(
            SETTINGS[3]["text"],
            reply_markup=ReplyKeyboardMarkup(SETTINGS[3]["keyboard"], one_time_keyboard=True),
            disable_web_page_preview=True,
        )
        return SETTING4
    settings = {
        SETTINGS[3]["name"]: True if answer == YES else False,
    }
    if answer != SKIP:
        tg_chat_id = update["message"]["chat"]["id"]
        update_team(tg_chat_id, settings=settings)
    update.message.reply_markdown(
        SETTINGS_FINISHED,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def cancel(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        CANCEL,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        f"{HELP_TEXT}{HELP_COMMAND_LIST}",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def issue(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        ISSUE,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def feedback(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        FEEDBACK,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def explain(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        EXPLAIN_TEXT,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def start_settings(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type != "group":
        return wrong_chat_type(update, context)
    team = update_team(update["message"]["chat"]["id"], settings={})
    if team is None:
        return team_not_exists(update, context)
    update.message.reply_markdown(
        START_SETTINGS + "\n" + SETTINGS[TEAM_ID]["text"],
        reply_markup=ReplyKeyboardMarkup(SETTINGS[TEAM_ID]["keyboard"], one_time_keyboard=True),
        disable_web_page_preview=True,
    )
    return SETTING1


def team_not_exists(update: Update, context: CallbackContext):
    context.bot.send_message(
        text=TEAM_NOT_IN_DB_TEXT,
        chat_id=update["message"]["chat"]["id"],
        parse_mode="Markdown",
    )
    return ConversationHandler.END


def wrong_chat_type(update: Update, context: CallbackContext):
    context.bot.send_message(
        text=NO_GROUP_CHAT,
        chat_id=update["message"]["chat"]["id"],
        parse_mode="Markdown",
    )
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

        states = {

            SETTING1: [MessageHandler(Filters.text & (~Filters.command), weekly_op_link), ],

            SETTING2: [MessageHandler(Filters.text & (~Filters.command), lineup_op_link), ],

            SETTING3: [MessageHandler(Filters.text & (~Filters.command), scheduling_suggestion), ],

            SETTING4: [MessageHandler(Filters.text & (~Filters.command), scheduling_confirmation), ],

        }

        start_states = {
            TEAM_ID: [MessageHandler(Filters.text & (~Filters.command), get_team_id), ],
        }

        fallbacks = [
            CommandHandler('cancel', cancel),
            CommandHandler("help", helpcommand),
            CommandHandler("issue", issue),
            CommandHandler("feedback", feedback),
            CommandHandler("bop", bop),
            CommandHandler("explain", explain),
        ]
        # Add conversation handler with the states TEAM_ID, SETTING1, SETTING2
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start, )],

            states=start_states,

            fallbacks=fallbacks
        )
        conv_handler_settings = ConversationHandler(
            entry_points=[CommandHandler('settings', start_settings, )],

            states=states,

            fallbacks=fallbacks
        )
        dp.add_handler(conv_handler)
        dp.add_handler(conv_handler_settings)
        for cmd in fallbacks[1:]:
            dp.add_handler(cmd)
        updater.start_polling()
        updater.idle()
