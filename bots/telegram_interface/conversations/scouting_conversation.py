from django.conf import settings
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, ConversationHandler
from bots.languages import de_DE as LanguagePack
from app_prime_league.models import Team, ScoutingWebsite
from bots.telegram_interface.keyboards import scouting_keyboard
from bots.utils import mysql_has_gone_away_decorator
from utils.messages_logger import log_command


@log_command
@mysql_has_gone_away_decorator
def scouting(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        update.message.reply_markdown(
            LanguagePack.TEAM_NOT_IN_DB_TEXT,
        )
        return ConversationHandler.END

    website_name = settings.DEFAULT_SCOUTING_NAME if not team.scouting_website else team.scouting_website.name
    text = f"{LanguagePack.WHICH_SCOUTING_WEBSITE}\n{LanguagePack.CURRENTLY}: _{website_name}_"

    update.message.reply_markdown(
        text=text,
        reply_markup=scouting_keyboard(),
    )


def finish_scouting(update: Update, context: CallbackContext, ):
    website_name = update.callback_query.data
    message = update.callback_query.message
    chat_id = message.chat_id
    try:
        team = Team.objects.get(telegram_id=chat_id)
    except Team.DoesNotExist:
        context.bot.edit_message_text(
            LanguagePack.TEAM_NOT_IN_DB_TEXT,
        )
        return ConversationHandler.END
    if website_name == "schließen":
        context.bot.edit_message_text(
            LanguagePack.IT_REMAINS_AS_IT_IS,
            chat_id=message.chat_id,
            message_id=message.message_id,
            reply_markup=None,
            parse_mode=ParseMode.MARKDOWN,

        )
        return ConversationHandler.END
    try:
        scouting_website = ScoutingWebsite.objects.get(name=website_name)
        team.scouting_website = scouting_website
        team.save()
    except ScoutingWebsite.DoesNotExist:
        team.scouting_website = None
        team.save()

    website_name = settings.DEFAULT_SCOUTING_NAME if not team.scouting_website else team.scouting_website.name
    context.bot.edit_message_text(
        LanguagePack.SET_SCOUTING.format(scouting_website=website_name),
        chat_id=message.chat_id,
        message_id=message.message_id,
        reply_markup=None,
        disable_web_page_preview=True,
    )
    return ConversationHandler.END
