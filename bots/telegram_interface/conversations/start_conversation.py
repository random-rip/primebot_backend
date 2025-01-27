from django.conf import settings
from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import ScoutingWebsite, Team
from app_prime_league.models.channel import Channel, ChannelTeam, Platforms
from bots.messages import MatchesOverview
from bots.telegram_interface.commands.single_commands import set_photo
from bots.telegram_interface.keyboards import boolean_keyboard
from utils.exceptions import (
    CouldNotParseURLException,
    Div1orDiv2TeamException,
    PrimeLeagueConnectionException,
    TeamWebsite404Exception,
)
from utils.messages_logger import log_callbacks, log_command
from utils.utils import get_valid_team_id


def channel_has_at_least_one_team(update: Update) -> ChannelTeam:
    return ChannelTeam.objects.filter(
        channel__platform=Platforms.TELEGRAM, channel__telegram_id=update.message.chat.id
    ).first()


# /start
@log_command
def start(update: Update, context: CallbackContext):
    chat_type = update.message.chat.type
    if chat_type not in ["group", "supergroup"]:
        update.message.reply_markdown(
            text=(
                "Hallo,\n"
                "Du möchtest den PrimeBot für Pushbenachrichtigungen benutzen?\n\n"
                "Erste Schritte:\n"
                "1️⃣ Erstelle einen Gruppen-Chat in Telegram und füge [mich]({start_link}) hinzu.\n"
                "2️⃣ Registriere dein Team im Gruppenchat mit /start.\n"
                "3️⃣ Personalisiere mit /settings deine Benachrichtigungen.\n\n"
                "Viel Erfolg auf den Richtfeldern! 🍀"
            ).format(start_link=settings.TELEGRAM_START_LINK),
            disable_web_page_preview=True,
        )
        return ConversationHandler.END
    if (channel_team := channel_has_at_least_one_team(update)) is not None:
        update.message.reply_markdown(
            text=(
                f"In diesem Chat ist bereits das Team *{channel_team.team.name}* registriert. "
                "Möchtest Du ein anderes Team für diesen Channel registrieren?\n"
                "Dann gib jetzt deine *Team-URL* oder deine *Team ID* an. Wenn nicht, benutze /cancel.\n\n"
                "Solltest Du Hilfe benötigen, benutze /help."
            ),
            disable_web_page_preview=True,
            quote=False,
        )
        return 1
    update.message.reply_markdown(
        text=(
            "Sternige Grüße,\n"
            "Du bist es Leid, jeden Tag auf den Prime League-Seiten mühsam nach neuen Updates zu suchen?\n"
            "Gut, dass ich hier bin: Ich werde dich zu allen Änderungen bei euren Spielen updaten. 📯\n\n"
            "Bitte kopiere dafür deine *TEAM_URL* oder deine *TEAM_ID* in den Chat."
        ),
        disable_web_page_preview=True,
        quote=False,
    )
    return 1


def team_exists(team_id):
    return Team.objects.filter(id=team_id).exists()


def team_has_chat_id(team_id):
    return Team.objects.filter(id=team_id, telegram_id__isnull=False).exists()


@log_command
def team_registration(update: Update, context: CallbackContext):
    try:
        team_id = get_valid_team_id(update.message.text)
    except CouldNotParseURLException:
        update.message.reply_markdown(
            text=(
                "Die angegebene URL entspricht nicht dem richtigen Format.\n"
                "Achte auf das richtige Format oder gib die *Team ID* ein.\n"
                "Bitte versuche es erneut oder benutze /cancel."
            ),
            quote=False,
        )
        return 1
    except Div1orDiv2TeamException:
        update.message.reply_markdown(
            text="Es können keine Teams aus Division 1 oder 2 registriert werden.",
            quote=False,
        )
        return 1
    chat_id = update.message.chat.id

    if ChannelTeam.objects.filter(
        channel__platform=Platforms.TELEGRAM,
        team_id=team_id,
        channel__telegram_id=chat_id,
    ).exists():
        update.message.reply_markdown(
            text="Das Team ist bereits in diesem Chat registriert. Bitte gib eine andere Team ID ein oder"
            " benutze /cancel.",
            quote=False,
        )
        return 1

    context.bot.send_message(
        text="Alles klar, ich schaue, was ich dazu finden kann.\nDas dauert circa 40 Sekunden... ⏳\n",
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN,
    )

    try:
        from app_prime_league.teams import register_team

        team = register_team(team_id=team_id)
    except TeamWebsite404Exception:
        update.message.reply_markdown(
            text=(
                "Die angegebene URL entspricht nicht dem richtigen Format.\n"
                "Achte auf das richtige Format oder gib die *Team ID* ein.\n"
                "Bitte versuche es erneut oder /cancel."
            ),
            quote=False,
        )
        return 1
    except PrimeLeagueConnectionException:
        update.message.reply_markdown(
            text=(
                "Momentan kann keine Verbindung zu der Prime League Website hergestellt werden. "
                "Probiere es in ein paar Stunden noch einmal.\n"
                "Wenn es später immer noch nicht funktioniert, schaue auf "
                "https://primebot.me/information/contact nach Hilfe."
            ),
            quote=False,
        )
        return ConversationHandler.END

    channel, created = Channel.objects.get_or_create(telegram_id=chat_id, platform=Platforms.TELEGRAM)
    if not created:
        channel.channel_teams.all().delete()

    ChannelTeam.objects.create(channel=channel, team=team)

    update.message.reply_markdown(
        text=(
            "Soll ich das Teambild aus der Prime League importieren?\n"
            "_Dazu werden Adminrechte hier in der Gruppe benötigt._"
        ),
        reply_markup=boolean_keyboard(0),
    )

    return ConversationHandler.END


@log_callbacks
def set_optional_photo(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id

    url = Team.objects.get(channels__platform=Platforms.TELEGRAM, channels__telegram_id=chat_id).logo_url
    successful = set_photo(chat_id, context, url)
    if successful:
        finish_registration(update, context)
    else:
        try:
            context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=(
                    "Profilbild konnte nicht geändert werden. Soll ich das Teambild aus der Prime League importieren?\n"
                    "_Dazu werden Adminrechte benötigt._"
                ),
                reply_markup=boolean_keyboard(0),
                parse_mode=ParseMode.MARKDOWN,
            )
        except BadRequest:
            pass


@log_callbacks
def finish_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    channel_team = ChannelTeam.objects.get(
        channel__telegram_id=chat_id,
    )

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text="✅ Okay",
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN,
    )

    context.bot.send_message(
        text=(
            "Dein registriertes Team:\n"
            "*{team_name}*\n"
            "Perfekt! Ich sende dir jetzt Benachrichtigungen in diese Gruppe, "
            "wenn es neue Updates zu euren Matches gibt. 🏆\n"
            "Du kannst noch mit /settings Benachrichtigungen personalisieren und "
            "die Scouting Website (Standard: {scouting_website}) ändern."
        ).format(team_name=channel_team.team.name, scouting_website=ScoutingWebsite.default().name),
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )

    msg = MatchesOverview(channel_team=channel_team)
    context.bot.send_message(
        text=msg.generate_message(),
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
