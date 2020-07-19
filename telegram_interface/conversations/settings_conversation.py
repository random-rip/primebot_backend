from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler

from app_prime_league.teams import update_team
from telegram_interface.messages import ENABLED, SETTINGS_MAIN_MENU, DISABLED, BOOLEAN_KEYBOARD_OPTIONS, CLOSE, \
    SETTINGS_FINISHED
from telegram_interface.validation_messages import wrong_chat_type, team_not_exists
from utils.log_wrapper import log_command, log_conversation

SETTINGS = {
    # 0 WEEKLY_OP_LINK
    "WEEKLY_OP_LINK": {
        "name": "weekly_op_link",
        "title": "Wochenübersicht",
        "text": "Möchtet ihr jede Woche eine neue Benachrichtigung für die kommende Spielwoche erhalten?",
        "callback_data": "1",
    },
    # 1 LINEUP_OP_LINK
    "LINEUP_OP_LINK": {
        "name": "lineup_op_link",
        "title": "Lineup",
        "text": "Möchtet ihr benachrichtigt werden, wenn der Gegner ein neues Lineup aufgestellt hat?",
        "callback_data": "2",
    },
    # 2 SCHEDULING_SUGGESTION
    "SCHEDULING_SUGGESTION": {
        "name": "scheduling_suggestion",
        "title": "Neue Zeitvorschläge",
        "text": "Möchtet ihr über neue Zeitvorschläge des Gegners informiert werden?",
        "callback_data": "3",
    },
    # 3 SCHEDULING_CONFIRMATION
    "SCHEDULING_CONFIRMATION": {
        "name": "scheduling_confirmation",
        "title": "Bestätigte Zeitvorschläge",
        "text": "Möchtet ihr bei der Bestätigung eines Zeitvorschlags benachrichtigt werden?",
        "callback_data": "4",
    },
    # 4 CHANGELOG_UPDATE
    "CHANGELOG_UPDATE": {
        "name": "changelog_update",
        "title": "Changelog",
        "text": "Möchtet ihr bei Änderungen am Bot benachrichtigt werden?",
        "callback_data": "5",
    },
}


# /settings
@log_command
def start_settings(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type != "group":
        return wrong_chat_type(update, context)
    team = update_team(update["message"]["chat"]["id"], settings={})
    if team is None:
        return team_not_exists(update, context)
    update.message.reply_text(
        SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard,
    )


@log_conversation
def main_settings_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard,
    )


@log_conversation
def main_settings_menu_close(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=SETTINGS_FINISHED,
        reply_markup=None,
    )


def _create_main_menu_keyboard():
    keyboards = [
        [
            InlineKeyboardButton(
                items["title"],
                callback_data=f"m{items['callback_data']}"
            )
        ] for items in SETTINGS.values()
    ]
    keyboards.append([InlineKeyboardButton(
        CLOSE,
        callback_data="close"
    )])

    return InlineKeyboardMarkup(keyboards)


main_menu_keyboard = _create_main_menu_keyboard()


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


class Setting:

    def __init__(self, name, title, text, callback_data):
        self.name = name
        self.title = title
        self.text = text
        self.callback_data = callback_data

        @log_conversation
        def enable(update: Update, context: CallbackContext):
            setting = {
                self.name: True,
            }
            query = update.callback_query
            tg_chat_id = query.message.chat.id
            update_team(tg_chat_id, settings=setting)
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"{self.title} {ENABLED}\n{SETTINGS_MAIN_MENU['text']}",
                reply_markup=main_menu_keyboard,
            )

        @log_conversation
        def disable(update: Update, context: CallbackContext):
            setting = {
                self.name: False,
            }
            query = update.callback_query
            tg_chat_id = query.message.chat.id
            update_team(tg_chat_id, settings=setting)
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"{self.title} {DISABLED}\n{SETTINGS_MAIN_MENU['text']}",
                reply_markup=main_menu_keyboard,
            )

        @log_conversation
        def show(update: Update, context: CallbackContext):
            query = update.callback_query
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=self.text,
                reply_markup=get_boolean_keyboard(self.callback_data)
            )

        self.enable = enable
        self.disable = disable
        self.show = show


callback_query_settings_handlers = []
for i, v in SETTINGS.items():
    setting = Setting(**v)
    setting_id = setting.callback_data
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.show, pattern=f'm{setting_id}'))
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.enable, pattern=f'{setting_id}enable'))
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.disable, pattern=f'{setting_id}disable'))
