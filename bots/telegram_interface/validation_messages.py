from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler


def channel_not_registered(update: Update, ):
    update.message.reply_markdown(
        text=(
            "In der Telegram-Gruppe wurde noch kein Team registriert (/start)."
        ),
    )
    return ConversationHandler.END


def wrong_chat_type(update: Update, context: CallbackContext):
    context.bot.send_message(
        text=(
            "Dieser Befehl kann nur in einer Telegram-Gruppe ausgeführt werden."
        ),
        chat_id=update["message"]["chat"]["id"],
        parse_mode=ParseMode.MARKDOWN,
    )
    return ConversationHandler.END
