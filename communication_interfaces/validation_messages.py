from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler

from communication_interfaces.languages.de_DE import TEAM_NOT_IN_DB_TEXT, NO_GROUP_CHAT


def team_not_exists(update: Update, context: CallbackContext):
    context.bot.send_message(
        text=TEAM_NOT_IN_DB_TEXT,
        chat_id=update["message"]["chat"]["id"],
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


def wrong_chat_type(update: Update, context: CallbackContext):
    context.bot.send_message(
        text=NO_GROUP_CHAT,
        chat_id=update["message"]["chat"]["id"],
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END
