import django.utils.translation
from django.conf import settings
from django.utils import translation
from django.utils.translation import gettext as _
from telegram import Update, ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from bots.languages.de_DE import (
    START_CHAT,
    WAIT_A_MOMENT_TEXT, TEAM_ID_NOT_VALID_TEXT, SET_PHOTO_TEXT,
    PHOTO_SUCCESS_TEXT, PHOTO_RETRY_TEXT, CHAT_EXISTING, TEAM_LOCKED, GROUP_REASSIGNED, TEAM_ID_NOT_CORRECT,
    PL_CONNECTION_ERROR
)
from bots.messages import MatchesOverview
from bots.telegram_interface.commands.single_commands import set_photo
from bots.telegram_interface.keyboards import boolean_keyboard
from bots.utils import mysql_has_gone_away_decorator
from utils.exceptions import CouldNotParseURLException, PrimeLeagueConnectionException, TeamWebsite404Exception
from utils.messages_logger import log_command, log_callbacks
from utils.utils import get_valid_team_id


def just_wait_a_moment(chat_id, context: CallbackContext):
    context.bot.send_message(
        text=WAIT_A_MOMENT_TEXT,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN,
    )


def get_existing_chat_id(update: Update):
    chat_id = get_chat_id(update)
    if Team.objects.filter(telegram_id=chat_id).exists():
        return chat_id
    return None


def get_chat_id(update: Update):
    return update.message.chat.id


def chat_id_exists_in_db(chat_id):
    return Team.objects.filter(telegram_id=chat_id).exists()


def team_is_locked(team_id):
    new_team = Team.objects.get_team(team_id)
    if new_team is None:
        return False
    new_team_settings = dict(new_team.setting_set.all().values_list("attr_name", "attr_value"))
    return new_team_settings.get("lock_team", True) and new_team.telegram_id is not None


# /start
@log_command
@mysql_has_gone_away_decorator
def start(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        update.message.reply_markdown(
            START_CHAT.format(start_link=settings.TELEGRAM_START_LINK),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return ConversationHandler.END
    if (get_existing_chat_id(update)) is None:

        print(django.utils.translation.check_for_language("de"))
        print(django.utils.translation.check_for_language("en"))
        print(django.utils.translation.check_for_language("es"))
        print(translation.gettext("Hallo Welt"))
        print(django.utils.translation.get_language())
        with translation.override("en"):
            print(django.utils.translation.get_language())
            print(translation.gettext("Hallo Welt"))

            update.message.reply_markdown(
                text=translation.gettext(
                    "Sternige Grüße,\n"
                    "Du bist es Leid, jeden Tag auf den Prime League-Seiten mühsam nach neuen Updates zu suchen?\n"
                    "Gut, dass ich hier bin: Ich werde dich zu allen Änderungen bei euren Spielen updaten. 📯\n\n"
                    "Bitte kopiere dafür deine *TEAM_URL* oder deine *TEAM_ID* in den Chat."
                ),
                disable_web_page_preview=True,
                quote=False,
            )
    else:
        update.message.reply_markdown(
            CHAT_EXISTING,
            disable_web_page_preview=True,
            quote=False,
        )
    return 1


def team_exists(team_id):
    return Team.objects.filter(id=team_id).exists()


def team_has_chat_id(team_id):
    return Team.objects.filter(id=team_id, telegram_id__isnull=False).exists()


@log_command
@mysql_has_gone_away_decorator
def team_registration(update: Update, context: CallbackContext):
    try:
        team_id = get_valid_team_id(update.message.text)
    except CouldNotParseURLException:
        update.message.reply_markdown(
            TEAM_ID_NOT_VALID_TEXT,
            quote=False,
        )
        return 1
    chat_id = get_chat_id(update)
    just_wait_a_moment(chat_id, context)

    if team_is_locked(team_id):
        update.message.reply_markdown(
            text=TEAM_LOCKED.format(team=Team.objects.get_team(team_id)),
            quote=False,
        )
        return ConversationHandler.END

    old_team = Team.objects.filter(telegram_id=chat_id).first()
    old_team_chat_id = None
    if chat_id_exists_in_db(chat_id) and team_has_chat_id(old_team.id):
        old_team_chat_id = old_team.telegram_id
        old_team.telegram_id = None
        old_team.save()
    new_team_old_chat_id = None

    if team_exists(team_id):
        new_team_old_chat_id = Team.objects.get_team(team_id).telegram_id

    try:
        new_team = register_team(team_id=team_id, telegram_id=chat_id)
    except PrimeLeagueConnectionException:
        update.message.reply_markdown(
            text=PL_CONNECTION_ERROR,
            quote=False,
        )
        return 1
    except TeamWebsite404Exception:
        update.message.reply_markdown(
            text=TEAM_ID_NOT_VALID_TEXT,
            quote=False,
        )
        return 1

    if new_team is None and old_team is not None:
        old_team.telegram_id = old_team_chat_id
        old_team.save()
        update.message.reply_markdown(
            text=TEAM_ID_NOT_CORRECT.format(id=team_id),
            disable_web_page_preview=True,
            quote=False,
        )
        return 1
    elif new_team is None:
        update.message.reply_markdown(
            text=TEAM_ID_NOT_CORRECT.format(id=team_id),
            disable_web_page_preview=True
        )
        return 1
    else:
        if new_team_old_chat_id is not None:
            update.message.reply_markdown(
                msg=GROUP_REASSIGNED.format(team=new_team),
                chat_id=new_team_old_chat_id,
                quote=False,
            )
        update.message.reply_markdown(
            SET_PHOTO_TEXT,
            reply_markup=boolean_keyboard(0),
        )

    return ConversationHandler.END


@log_callbacks
@mysql_has_gone_away_decorator
def set_optional_photo(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    url = Team.objects.get(telegram_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        finish_registration(update, context)
    else:
        try:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=PHOTO_RETRY_TEXT,
                reply_markup=boolean_keyboard(0),
                parse_mode=ParseMode.MARKDOWN,
            )
        except BadRequest:
            pass


@log_callbacks
@mysql_has_gone_away_decorator
def finish_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    team = Team.objects.get(telegram_id=chat_id)
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=PHOTO_SUCCESS_TEXT,
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN,

    )

    context.bot.send_message(
        text=_(
            "Dein registriertes Team:\n"
            "*{team.name}*\n"
            "Perfekt! Ich sende dir jetzt Benachrichtigungen in diese Gruppe, "
            "wenn es neue Updates zu euren Matches gibt. 🏆\n"
            "Du kannst noch mit /settings Benachrichtigungen personalisieren und "
            "die Scouting Website (Standard: {}) ändern."
        ),
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )

    msg = MatchesOverview(team=team)
    context.bot.send_message(
        text=msg.message,
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
