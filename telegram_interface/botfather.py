from itertools import chain

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.filters import Filters
import requests

from app_prime_league.teams import register_team, update_team
from prime_league_bot import settings
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, ConversationHandler, \
    CallbackQueryHandler

from telegram_interface.messages import START_GROUP, START_CHAT, HELP_COMMAND_LIST, SETTINGS_FINISHED, ISSUE, \
    FEEDBACK, START_SETTINGS, TEAM_EXISTING, SETTINGS, CANCEL, SKIP, YES, TEAM_ID_VALID, HELP_TEXT, REGISTRATION_FINISH, \
    WAIT_A_MOMENT_TEXT, EXPLAIN_TEXT, NO_GROUP_CHAT, TEAM_NOT_IN_DB_TEXT, TEAM_ID_NOT_VALID_TEXT, SETTINGS_MAIN_MENU, \
    BOOLEAN_KEYBOARD_OPTIONS, ENABLED, DISABLED

TEAM_ID, SETTING1, SETTING2, SETTING3, SETTING4 = range(5)


def start(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type == "group":
        update.message.reply_markdown(START_GROUP, disable_web_page_preview=True)
        return TEAM_ID
    else:
        update.message.reply_markdown(START_CHAT, parse_mode="Markdown", disable_web_page_preview=True)
        return ConversationHandler.END


def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    chat_id = update.message.chat_id
    bot = context.bot
    bot.send_photo(chat_id=chat_id, photo=url)


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
        return ConversationHandler.END


def start_settings(update: Update, context: CallbackContext):
    update.message.reply_text(
        SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard(),
    )


def main_settings_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard(),
    )


def all_settings(update: Update, context: CallbackContext, setting):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=setting["text"],
        reply_markup=get_boolean_keyboard(setting["callback_data"]),
    )


def all_settings_enable(update: Update, context: CallbackContext, sett):
    setting = {
        sett["name"]: True,
    }
    query = update.callback_query
    tg_chat_id = query.message.chat.id
    update_team(tg_chat_id, settings=setting)
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"{sett['title']} {ENABLED}\n{SETTINGS_MAIN_MENU['text']}",
        reply_markup=main_menu_keyboard(),
    )


def all_settings_disable(update: Update, context: CallbackContext, sett):
    setting = {
        sett["name"]: False,
    }
    query = update.callback_query
    tg_chat_id = query.message.chat.id
    update_team(tg_chat_id, settings=setting)
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=f"{sett['title']} {DISABLED}\n{SETTINGS_MAIN_MENU['text']}",
        reply_markup=main_menu_keyboard(),
    )

############################ Settings #########################################

def setting1(update: Update, context: CallbackContext):
    all_settings(update, context, SETTINGS[0])


def setting1_enable(update: Update, context: CallbackContext):
    all_settings_enable(update, context, SETTINGS[0])


def setting1_disable(update: Update, context: CallbackContext):
    all_settings_disable(update, context, SETTINGS[0])


def setting2(update: Update, context: CallbackContext):
    all_settings(update, context, SETTINGS[1])


def setting2_enable(update: Update, context: CallbackContext):
    all_settings_enable(update, context, SETTINGS[1])


def setting2_disable(update: Update, context: CallbackContext):
    all_settings_disable(update, context, SETTINGS[1])


def setting3(update: Update, context: CallbackContext):
    all_settings(update, context, SETTINGS[2])


def setting3_enable(update: Update, context: CallbackContext):
    all_settings_enable(update, context, SETTINGS[2])


def setting3_disable(update: Update, context: CallbackContext):
    all_settings_disable(update, context, SETTINGS[2])


def setting4(update: Update, context: CallbackContext):
    all_settings(update, context, SETTINGS[3])


def setting4_enable(update: Update, context: CallbackContext):
    all_settings_enable(update, context, SETTINGS[3])


def setting4_disable(update: Update, context: CallbackContext):
    all_settings_disable(update, context, SETTINGS[3])


############################ Keyboards #########################################
def main_menu_keyboard():
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(setting["title"], callback_data=f"m{setting['callback_data']}")] for setting in SETTINGS
    ])
    return reply_markup


def get_boolean_keyboard(callback_data_prefix):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            BOOLEAN_KEYBOARD_OPTIONS[0]["title"],
            callback_data=f"{callback_data_prefix}enable"
            # f"{callback_data_prefix}_{BOOLEAN_KEYBOARD_OPTIONS[0]['callback_data']}",
        )],
        [InlineKeyboardButton(
            BOOLEAN_KEYBOARD_OPTIONS[1]["title"],
            callback_data=f"{callback_data_prefix}disable"
            # f"{callback_data_prefix}_{BOOLEAN_KEYBOARD_OPTIONS[1]['callback_data']}",
        )],
        # Main
        [InlineKeyboardButton(
            BOOLEAN_KEYBOARD_OPTIONS[2]["title"],
            callback_data="main",
        )],
    ])
    return reply_markup


############################# Messages #########################################
def main_menu_message():
    return 'Choose the option in main menu:'


def first_menu_message():
    return 'Choose the submenu in first menu:'


def second_menu_message():
    return 'Choose the submenu in second menu:'


class BotFather:
    """
    Botfather Class. Provides Communication with Bot(Telegram API) and Client
    """

    def __init__(self):
        self.api_key = settings.TELEGRAM_BOT_KEY

    def run(self):
        updater = Updater(settings.TELEGRAM_BOT_KEY, use_context=True, )
        # Allgemeine Commands
        updater.dispatcher.add_handler(CommandHandler('bop', bop))

        # Main Menu
        updater.dispatcher.add_handler(CommandHandler('start_settings_test', start_settings))
        updater.dispatcher.add_handler(CallbackQueryHandler(main_settings_menu, pattern='main'))
        # Setting 1
        updater.dispatcher.add_handler(CallbackQueryHandler(setting1, pattern='m1'))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting1_enable, pattern="1enable"))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting1_disable, pattern="1disable"))
        # Setting 2
        updater.dispatcher.add_handler(CallbackQueryHandler(setting2, pattern='m2'))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting2_enable, pattern="2enable"))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting2_disable, pattern="2disable"))
        # Setting 3
        updater.dispatcher.add_handler(CallbackQueryHandler(setting3, pattern='m3'))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting3_enable, pattern="3enable"))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting3_disable, pattern="3disable"))
        # Setting 4
        updater.dispatcher.add_handler(CallbackQueryHandler(setting4, pattern='m4'))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting4_enable, pattern="4enable"))
        updater.dispatcher.add_handler(CallbackQueryHandler(setting4_disable, pattern="4disable"))

        updater.start_polling()
