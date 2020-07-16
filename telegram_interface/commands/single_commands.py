import os
import urllib.request

import requests
from django.core.files import File
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from telegram_interface.messages import HELP_COMMAND_LIST, ISSUE, \
    FEEDBACK, CANCEL, HELP_TEXT, EXPLAIN_TEXT
from utils.log_wrapper import log_command


def set_photo(update: Update, context: CallbackContext, url):
    chat_id = update.message.chat_id
    bot_id = context.bot.id
    bot_info = context.bot.get_chat_member(chat_id=chat_id, user_id=bot_id)
    if not bot_info.can_change_info:
        return

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
        print("File nicht gefunden")


# /bop
@log_command
def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    chat_id = update.message.chat_id
    bot = context.bot
    bot.send_photo(chat_id=chat_id, photo=url)
    set_photo(update, context, url)


# /cancel
@log_command
def cancel(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        CANCEL,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /help
@log_command
def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        f"{HELP_TEXT}{HELP_COMMAND_LIST}",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /issue
@log_command
def issue(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        ISSUE,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /feedback
@log_command
def feedback(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        FEEDBACK,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /explain
@log_command
def explain(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        EXPLAIN_TEXT,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END
