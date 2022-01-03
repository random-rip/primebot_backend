import logging
import os
import random
import urllib.request

import requests
import telegram
from django.conf import settings
from django.core.files import File
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from app_api.modules.team_settings.maker import SettingsMaker
from app_prime_league.models import Team
from bots.languages import de_DE as LaP
from bots.messages import MatchesOverview
from bots.telegram_interface.validation_messages import team_not_exists
from bots.utils import mysql_has_gone_away_decorator
from prime_league_bot.settings import STORAGE_DIR
from utils.changelogs import CHANGELOGS
from utils.messages_logger import log_command

logger = logging.getLogger("notifications")


def set_photo(chat_id, context: CallbackContext, url):
    bot_id = context.bot.id
    bot_info = context.bot.get_chat_member(chat_id=chat_id, user_id=bot_id)
    if not bot_info.can_change_info:
        return False

    try:
        file_name = os.path.join(STORAGE_DIR, f"temp_{chat_id}.temp")
        _ = urllib.request.urlretrieve(url, file_name)
        with open(file_name, 'rb') as f:
            context.bot.set_chat_photo(
                chat_id=chat_id,
                photo=File(f),
                timeout=20,
            )
        os.remove(file_name)
    except (FileNotFoundError, telegram.error.BadRequest) as e:
        return False
    except Exception as e:
        logger.exception(e)
        return False
    return True


# /set_logo
@log_command
@mysql_has_gone_away_decorator
def set_logo(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if not Team.objects.filter(telegram_id=chat_id).exists():
        update.message.reply_markdown(
            LaP.TEAM_NOT_IN_DB_TEXT,
        )
        return ConversationHandler.END
    url = Team.objects.get(telegram_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        update.message.reply_markdown(
            LaP.PHOTO_SUCESS_TEXT,
        )
    else:
        update.message.reply_markdown(
            LaP.PHOTO_ERROR_TEXT,
        )
    return ConversationHandler.END


# /bop
@log_command
def bop(update: Update, context: CallbackContext):
    x = random.randrange(2)
    if x == 0:  # if settings.PREFERRED_ANIMAL == 'dog'
        contents = requests.get('https://api.thedogapi.com/v1/images/search?mime_types=gif').json()
        url = contents[0]['url']
    if x == 1:  # if settings.PREFERRED_ANIMAL == 'cat'
        url = 'https://cataas.com/cat/gif'
    chat_id = update.message.chat.id
    bot = context.bot
    try:
        bot.send_animation(chat_id=chat_id, animation=url)
    except Exception as e:
        logger.exception(e)


# /cancel
@log_command
def cancel(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        LaP.CANCEL,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /help
@log_command
def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        f"{LaP.HELP_TEXT}{LaP.HELP_COMMAND_LIST}",
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /issue
@log_command
def issue(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        LaP.ISSUE,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /feedback
@log_command
def feedback(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        LaP.FEEDBACK,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /explain
@log_command
def explain(update: Update, context: CallbackContext):
    log = CHANGELOGS[sorted(CHANGELOGS.keys())[-1]]
    update.message.reply_markdown(
        LaP.EXPLAIN_TEXT.format(version=log["version"]),
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
@mysql_has_gone_away_decorator
def overview(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        update.message.reply_markdown(
            LaP.TEAM_NOT_IN_DB_TEXT,
        )
        return ConversationHandler.END

    msg = MatchesOverview(team=team)
    update.message.reply_markdown(
        msg.message,
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /set_logo
@log_command
@mysql_has_gone_away_decorator
def delete(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if not Team.objects.filter(telegram_id=chat_id).exists():
        update.message.reply_markdown(
            LaP.TEAM_NOT_IN_DB_TEXT,
        )
        return ConversationHandler.END
    team = Team.objects.get(telegram_id=chat_id)
    team.set_telegram_null()
    update.message.reply_markdown(
        LaP.TG_DELETE,
    )
    return ConversationHandler.END


@log_command
@mysql_has_gone_away_decorator
def team_settings(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        team_not_exists(update, context)
        return ConversationHandler.END

    maker = SettingsMaker(team=team)
    link = maker.generate_expiring_link(platform="telegram")
    update.message.reply_markdown(
        LaP.TG_SETTINGS_LINK.format(link=link, team=team.name, minutes=settings.TEMP_LINK_TIMEOUT_MINUTES),
        disable_web_page_preview=True,
        quote=False
    )
    return ConversationHandler.END
