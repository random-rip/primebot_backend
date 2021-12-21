from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import CallbackContext, CallbackQueryHandler

from app_prime_league.models import Setting, Team
from app_prime_league.teams import update_settings
from bots.languages.de_DE import ENABLED, SETTINGS_MAIN_MENU, DISABLED, BOOLEAN_KEYBOARD_OPTIONS, CLOSE, \
    SETTINGS_FINISHED, CURRENTLY
from bots.utils import mysql_has_gone_away_decorator
from bots.telegram_interface.validation_messages import wrong_chat_type, team_not_exists
from utils.messages_logger import log_command, log_callbacks

SETTINGS = {
    # WEEKLY_OP_LINK
    "WEEKLY_OP_LINK": {
        "name": "weekly_op_link",
        "title": "Wochenübersicht",
        "text": "Möchtet ihr jede Woche eine neue Benachrichtigung für die kommende Spielwoche erhalten?",
        "callback_data": "1",
    },
    # PIN_WEEKLY_OP_LINK
    "PIN_WEEKLY_OP_LINK": {
        "name": "pin_weekly_op_link",
        "title": "Wochenübersicht anheften",
        "text": "Möchtet ihr, dass die wöchentliche Benachrichtigung angeheftet wird?\n"
                "(Dazu werden Admin- oder Pinrechte benötigt)",
        "callback_data": "6",
    },
    # LINEUP_OP_LINK
    "LINEUP_OP_LINK": {
        "name": "lineup_op_link",
        "title": "Lineup",
        "text": "Möchtet ihr benachrichtigt werden, wenn der Gegner ein neues Lineup aufgestellt hat?",
        "callback_data": "2",
    },
    # SCHEDULING_SUGGESTION
    "SCHEDULING_SUGGESTION": {
        "name": "scheduling_suggestion",
        "title": "Neue Zeitvorschläge",
        "text": "Möchtet ihr über neue Zeitvorschläge des Gegners informiert werden?",
        "callback_data": "3",
    },
    # SCHEDULING_CONFIRMATION
    "SCHEDULING_CONFIRMATION": {
        "name": "scheduling_confirmation",
        "title": "Bestätigte Zeitvorschläge",
        "text": "Möchtet ihr bei der Bestätigung eines Zeitvorschlags benachrichtigt werden?",
        "callback_data": "4",
    },
    # CHANGELOG_UPDATE
    "CHANGELOG_UPDATE": {
        "name": "changelog_update",
        "title": "Bot Patches",
        "text": "Möchtet ihr bei Patches am Bot benachrichtigt werden?",
        "callback_data": "5",
    },
    # UNLOCK_BOT
    "LOCK_Team": {
        "name": "lock_team",
        "title": "Team-Sperre",
        "text": "Möchtet ihr, dass euer Team in einem anderen Chat *nicht* neu initialisiert werden darf?",
        "callback_data": "7",
    },
}


# /settings
@log_command
@mysql_has_gone_away_decorator
def start_settings(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        return wrong_chat_type(update, context)
    team = update_settings(update.message.chat.id, settings={})
    if team is None:
        return team_not_exists(update, context)
    update.message.reply_text(
        SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard,
        parse_mode=ParseMode.MARKDOWN
    )


@log_callbacks
@mysql_has_gone_away_decorator
def main_settings_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=SETTINGS_MAIN_MENU["text"],
        reply_markup=main_menu_keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


@log_callbacks
@mysql_has_gone_away_decorator
def main_settings_menu_close(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=SETTINGS_FINISHED,
        reply_markup=None,
    )


@mysql_has_gone_away_decorator
def migrate_chat(update: Update, context: CallbackContext):
    if update.message.chat.type == "supergroup":
        return
    try:
        old_chat_id = update.message.chat.id
        team = Team.objects.get(telegram_id=old_chat_id)
    except Team.DoesNotExist as e:
        return
    new_chat_id = update.message.migrate_to_chat_id
    team.telegram_id = new_chat_id
    team.save()


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


class NotificationSetting:

    def __init__(self, name, title, text, callback_data):
        self.name = name
        self.title = title
        self.text = text
        self.callback_data = callback_data

        @log_callbacks
        def enable(update: Update, context: CallbackContext):
            setting = {
                self.name: True,
            }
            query = update.callback_query
            tg_chat_id = query.message.chat.id
            update_settings(tg_chat_id, settings=setting)
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"{self.title} {ENABLED}\n{SETTINGS_MAIN_MENU['text']}",
                reply_markup=main_menu_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )

        @log_callbacks
        def disable(update: Update, context: CallbackContext):
            setting = {
                self.name: False,
            }
            query = update.callback_query
            tg_chat_id = query.message.chat.id
            update_settings(tg_chat_id, settings=setting)
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"{self.title} {DISABLED}\n{SETTINGS_MAIN_MENU['text']}",
                reply_markup=main_menu_keyboard,
                parse_mode=ParseMode.MARKDOWN,
            )

        @log_callbacks
        def show(update: Update, context: CallbackContext):
            query = update.callback_query
            team_id = Team.objects.get(telegram_id=query.message.chat.id).id
            setting_model_disabled = Setting.objects.filter(team_id=team_id, attr_name=self.name, attr_value=0).first()
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=f"{self.text} \n"
                     f"{CURRENTLY}: "
                     f"_{DISABLED if setting_model_disabled is not None else ENABLED}_",
                reply_markup=get_boolean_keyboard(self.callback_data),
                parse_mode=ParseMode.MARKDOWN,
            )

        self.enable = enable
        self.disable = disable
        self.show = show


callback_query_settings_handlers = []
for i, v in SETTINGS.items():
    setting = NotificationSetting(**v)
    setting_id = setting.callback_data
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.show, pattern=f'm{setting_id}'))
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.enable, pattern=f'{setting_id}enable'))
    callback_query_settings_handlers.append(CallbackQueryHandler(setting.disable, pattern=f'{setting_id}disable'))
