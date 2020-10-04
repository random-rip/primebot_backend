from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from communication_interfaces import send_message
from communication_interfaces.languages.de_DE import (
    START_GROUP, START_CHAT, TEAM_ID_VALID, REGISTRATION_FINISH,
    WAIT_A_MOMENT_TEXT, TEAM_ID_NOT_VALID_TEXT, SET_PHOTO_TEXT,
    PHOTO_SUCESS_TEXT, PHOTO_RETRY_TEXT, CHAT_EXISTING, TEAM_LOCKED, GROUP_REASSIGNED, TEAM_ID_NOT_CORRECT
)
from communication_interfaces.telegram_interface.commands.single_commands import set_photo
from communication_interfaces.telegram_interface.keyboards import boolean_keyboard
from utils.messages_logger import log_command, log_callbacks


def chat_reassignment(update: Update, context: CallbackContext):
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
            return 2
    chat_id = update.message.chat.id
    old_team = Team.objects.get(telegram_id=chat_id)
    new_team = Team.objects.filter(id=team_id).first()
    if new_team is None:
        new_team = register_team(team_id=team_id)
        if new_team is None:
            update.message.reply_markdown(
                text=TEAM_ID_NOT_VALID_TEXT,
            )
            return 2
    new_team_settings = dict(new_team.setting_set.all().values_list("attr_name", "attr_value"))
    if new_team_settings.get("lock_team", True) and new_team.telegram_id is not None:
        update.message.reply_markdown(
            TEAM_LOCKED,
        )
        return ConversationHandler.END
    old_team.telegram_id = None
    old_team.save()
    new_team.telegram_id = chat_id
    new_team.save()
    update.message.reply_markdown(
        text=f"{TEAM_ID_VALID}*{new_team.name}*\n{REGISTRATION_FINISH}",
    )
    return ConversationHandler.END


def get_valid_team_id(response, update: Update):
    try:
        team_id = int(response)
    except Exception as e:
        try:
            team_id = int(response.split("/teams/")[-1].split("-")[0])
        except Exception as e:
            update.message.reply_markdown(
                TEAM_ID_NOT_VALID_TEXT,
            )
            return None
    return team_id


def just_wait_a_moment(chat_id, context: CallbackContext):
    context.bot.tg_send_message(
        text=WAIT_A_MOMENT_TEXT,
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN,
    )


def get_existing_chat_id(update: Update):
    if Team.objects.filter(telegram_id=(chat_id := update.message.chat.id)).exists():
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
def start(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        update.message.reply_markdown(START_CHAT, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
        return ConversationHandler.END
    if (get_existing_chat_id(update)) is None:
        update.message.reply_markdown(
            START_GROUP,
            disable_web_page_preview=True
        )
    else:
        update.message.reply_markdown(
            CHAT_EXISTING,
            disable_web_page_preview=True
        )
    return 1


def team_exists(team_id):
    return Team.objects.filter(id=team_id).exists()


def team_has_chat_id(team_id):
    return Team.objects.filter(id=team_id, telegram_id__isnull=False).exists()


@log_command
def team_registration(update: Update, context: CallbackContext):
    team_id = get_valid_team_id(update.message.text, update)
    if team_id is None:
        return 1
    chat_id = get_chat_id(update)
    just_wait_a_moment(chat_id, context)

    if team_is_locked(team_id):
        update.message.reply_markdown(
            text=TEAM_LOCKED.format(team=Team.objects.get_team(team_id))
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

    new_team = register_team(team_id=team_id, telegram_id=chat_id)

    if new_team is None and old_team is not None:
        old_team.telegram_id = old_team_chat_id
        old_team.save()
        update.message.reply_markdown(
            text=TEAM_ID_NOT_CORRECT.format(id=team_id),
            disable_web_page_preview=True
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
            send_message(
                msg=GROUP_REASSIGNED.format(team=new_team),
                chat_id=new_team_old_chat_id,
                parse_mode=ParseMode.MARKDOWN
            )
        update.message.reply_markdown(
            SET_PHOTO_TEXT,
            reply_markup=boolean_keyboard(0),
        )

    return ConversationHandler.END


@log_callbacks
def set_optional_photo(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    url = Team.objects.get(telegram_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        finish_registration(update, context)
    else:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=PHOTO_RETRY_TEXT,
            reply_markup=boolean_keyboard(0),
            parse_mode=ParseMode.MARKDOWN,
        )


@log_callbacks
def finish_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    team = Team.objects.get(telegram_id=chat_id)
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=PHOTO_SUCESS_TEXT,
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN,

    )

    context.bot.tg_send_message(
        text=f"{TEAM_ID_VALID}*{team.name}*\n{REGISTRATION_FINISH}",
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
