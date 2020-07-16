from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.teams import register_team
from telegram_interface.messages import START_GROUP, START_CHAT, TEAM_EXISTING, TEAM_ID_VALID, REGISTRATION_FINISH, \
    WAIT_A_MOMENT_TEXT, TEAM_ID_NOT_VALID_TEXT
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


@log_conversation
def get_team_id(update: Update, context: CallbackContext):
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
            f"{TEAM_ID_VALID}*{team.name}*\n{REGISTRATION_FINISH}",
            reply_markup=ReplyKeyboardRemove(),
            disable_web_page_preview=True,
        )
        return ConversationHandler.END
