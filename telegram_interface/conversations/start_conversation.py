from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import Team
from app_prime_league.teams import register_team
from telegram_interface.commands.single_commands import set_photo
from telegram_interface.keyboards import boolean_keyboard
from telegram_interface.messages import START_GROUP, START_CHAT, TEAM_EXISTING, TEAM_ID_VALID, REGISTRATION_FINISH, \
    WAIT_A_MOMENT_TEXT, TEAM_ID_NOT_VALID_TEXT, GENERAL_TEAM_LINK, SET_PHOTO_TEXT, \
    PHOTO_SUCESS_TEXT, PHOTO_RETRY_TEXT
from utils.log_wrapper import log_command, log_conversation


# /start
@log_command
def start(update: Update, context: CallbackContext):
    chat_type = update["message"]["chat"]["type"]
    if chat_type == "group":
        update.message.reply_markdown(START_GROUP, disable_web_page_preview=True)
        return 1
    else:
        update.message.reply_markdown(START_CHAT, parse_mode="Markdown", disable_web_page_preview=True)
        return ConversationHandler.END


@log_command
def team_registration(update: Update, context: CallbackContext):
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
            return 1

    tg_group_id = update["message"]["chat"]["id"]
    context.bot.send_message(
        text=WAIT_A_MOMENT_TEXT,
        chat_id=tg_group_id,
        parse_mode="Markdown",
    )
    team = register_team(team_id=team_id, tg_group_id=tg_group_id)
    if team is None:
        update.message.reply_markdown(
            TEAM_EXISTING,
            disable_web_page_preview=True,
        )
        return 1
    else:
        update.message.reply_markdown(
            SET_PHOTO_TEXT,
            reply_markup=boolean_keyboard(0),
        )
        return ConversationHandler.END


@log_conversation
def set_optional_photo(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    url = Team.objects.get(telegram_channel_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        finish_registration(update, context)
    else:
        context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=PHOTO_RETRY_TEXT,
            reply_markup=boolean_keyboard(0),
            parse_mode="Markdown",
        )


@log_conversation
def finish_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    team = Team.objects.get(telegram_channel_id=chat_id)
    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=PHOTO_SUCESS_TEXT,
        reply_markup=None,
        parse_mode="Markdown",

    )

    context.bot.send_message(
        text=f"{TEAM_ID_VALID}*{team.name}*\n{REGISTRATION_FINISH}",
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )
