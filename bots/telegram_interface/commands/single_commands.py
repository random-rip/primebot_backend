import logging
import os
import urllib.request

import telegram
from django.conf import settings
from django.core.files import File
from django.utils.translation import gettext as _
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import Team
from bots.base.bop import GIFinator
from bots.messages import MatchesOverview, MatchOverview
from bots.telegram_interface.validation_messages import channel_not_registered
from core.settings_maker import SettingsMaker
from utils.messages_logger import log_command

logger = logging.getLogger("commands")


def set_photo(chat_id, context: CallbackContext, url):
    bot_id = context.bot.id
    bot_info = context.bot.get_chat_member(chat_id=chat_id, user_id=bot_id)
    if not bot_info.can_change_info:
        return False

    try:
        file_name = os.path.join(settings.STORAGE_DIR, f"temp_{chat_id}.temp")
        _ = urllib.request.urlretrieve(url, file_name)
        with open(file_name, 'rb') as f:
            context.bot.set_chat_photo(
                chat_id=chat_id,
                photo=File(f),
                timeout=20,
            )
        os.remove(file_name)
    except (FileNotFoundError, telegram.error.BadRequest):
        return False
    except Exception as e:
        logger.exception(e)
        return False
    return True


# /set_logo
@log_command
def set_logo(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if not Team.objects.filter(telegram_id=chat_id).exists():
        return channel_not_registered(update)
    url = Team.objects.get(telegram_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        update.message.reply_markdown(
            text="✅ Okay",
        )
    else:
        update.message.reply_markdown(
            text="Bild konnte nicht gesetzt werden.",
        )
    return ConversationHandler.END


# /bop
@log_command
def bop(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    bot = context.bot
    try:
        url = GIFinator.get_gif()
    except ConnectionError:
        bot.send_message(chat_id=chat_id, text="It's not my fault but I can't give you your surprise. :(")
        return
    try:
        bot.send_animation(chat_id=chat_id, animation=url)
    except Exception as e:
        logger.exception(e)


# /cancel
@log_command
def cancel(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        text=("Vorgang abgebrochen.\n" "Wenn Du Hilfe brauchst, benutze /help. 🔍"),
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


# /help
@log_command
def helpcommand(update: Update, context: CallbackContext):
    update.message.reply_markdown(
        text=(
            "Überblick:\n"
            "/start - um euer Team zu registrieren\n"
            "/settings - um die Einstellungen fürs Team zu bearbeiten\n"
            "/matches - um eine Übersicht der offenen Matches zu erhalten\n"
            "/delete - um euer registrierter Team aus der Gruppe zu entfernen\n"
            "/bop - What's boppin'?\n"
            "/cancel - um den aktuellen Vorgang abzubrechen\n"
            "/set\\_logo - um das Gruppenbild zu aktualisieren (Logo von der Prime League)\n"
        ),
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


@log_command
def matches(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        return channel_not_registered(update)

    msg = MatchesOverview(team=team)
    update.message.reply_markdown(
        msg.generate_message(),
        reply_markup=ReplyKeyboardRemove(),
        disable_web_page_preview=True,
    )
    return ConversationHandler.END


class InvalidMatchDay(Exception):
    pass


@log_command
def match(update: Update, context: CallbackContext) -> int:
    return call_match(update, context)


def call_match(update: Update, context: CallbackContext) -> int:
    user_command = update.message.text

    try:
        match_day = get_match_day(user_command)
    except InvalidMatchDay:
        update.message.reply_markdown(
            _("Invalid match day. Try using /match 1."),
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True,
        )
        return ConversationHandler.END

    chat_id = update.message.chat.id

    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        return channel_not_registered(update)

    found_matches = team.get_obvious_matches_based_on_stage(match_day=match_day)

    if not found_matches:
        update.message.reply_markdown(
            _("Sadly there is no match on the given match day."),
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True,
        )
        return ConversationHandler.END

    for i in found_matches:
        msg = MatchOverview(team=team, match=i)
        update.message.reply_markdown(
            msg.generate_message(),
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True,
        )

    return ConversationHandler.END


def get_match_day(user_command: str) -> int:
    command_args = user_command.split()[1:]

    if len(command_args) != 1:
        raise InvalidMatchDay

    possible_match_day = command_args[0]
    return get_validated_match_day(possible_match_day)


def get_validated_match_day(possible_match_day: str) -> int:
    try:
        return int(possible_match_day)
    except ValueError:
        raise InvalidMatchDay


@log_command
def delete(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    if not Team.objects.filter(telegram_id=chat_id).exists():
        return channel_not_registered(update)
    team = Team.objects.get(telegram_id=chat_id)
    team.set_telegram_null()
    update.message.reply_markdown(
        text=(
            "Alles klar, ich habe alle Verknüpfungen zu dieser Gruppe und dem Team gelöscht. "
            "Gebt uns gerne Feedback, falls euch Funktionalitäten fehlen oder nicht gefallen. Bye! ✌\n"
            "_Das Team kann jetzt in einem anderen Channel registriert werden, "
            "oder ein anderes Team kann in diesem Channel registriert werden._"
        ),
    )
    return ConversationHandler.END


@log_command
def team_settings(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        team = Team.objects.get(telegram_id=chat_id)  # noqa
    except Team.DoesNotExist:
        channel_not_registered(update)
        return ConversationHandler.END

    maker = SettingsMaker(team=team)
    link = maker.generate_expiring_link(platform="telegram")
    title = "Einstellungen für {team} ändern".format(team=team.name)
    content = ("Der Link ist nur {minutes} Minuten gültig. Danach muss ein neuer Link generiert werden.").format(
        minutes=settings.TEMP_LINK_TIMEOUT_MINUTES
    )

    update.message.reply_markdown(
        f"[{title}]({link})\n_{content}_",
        disable_web_page_preview=True,
        quote=False,
    )
    return ConversationHandler.END


def migrate_chat(update: Update, context: CallbackContext):
    if update.message.chat.type == "supergroup":
        return
    try:
        old_chat_id = update.message.chat.id
        team = Team.objects.get(telegram_id=old_chat_id)
    except Team.DoesNotExist:
        return
    new_chat_id = update.message.migrate_to_chat_id
    team.telegram_id = new_chat_id
    team.save()
