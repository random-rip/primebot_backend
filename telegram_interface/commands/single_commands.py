import os
import urllib.request

import requests
from django.core.files import File
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import Team
from prime_league_bot.settings import STORAGE_DIR
from telegram_interface.messages import HELP_COMMAND_LIST, ISSUE, \
    FEEDBACK, CANCEL, HELP_TEXT, EXPLAIN_TEXT, PHOTO_SUCESS_TEXT, PHOTO_ERROR_TEXT
from utils.log_wrapper import log_command


def set_photo(chat_id, context: CallbackContext, url):
    bot_id = context.bot.id
    bot_info = context.bot.get_chat_member(chat_id=chat_id, user_id=bot_id)
    if not bot_info.can_change_info:
        return False

    file_name = os.path.join(STORAGE_DIR, f"temp_{chat_id}.temp")
    _ = urllib.request.urlretrieve(url, file_name)

    try:
        with open(file_name, 'rb') as f:
            context.bot.set_chat_photo(
                chat_id=chat_id,
                photo=File(f),
                timeout=30,
                type="a",
            )
    except FileNotFoundError as e:
        print("File nicht gefunden")
        return False
    return True


# /set_logo
@log_command
def set_logo(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    url = Team.objects.get(telegram_channel_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        update.message.reply_markdown(
            PHOTO_SUCESS_TEXT,
        )
    else:
        update.message.reply_markdown(
            PHOTO_ERROR_TEXT,
        )
    return ConversationHandler.END


# /bop
@log_command
def bop(update: Update, context: CallbackContext):
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    chat_id = update.message.chat.id
    bot = context.bot
    bot.send_photo(chat_id=chat_id, photo=url)
    set_photo(chat_id, context, url)


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
