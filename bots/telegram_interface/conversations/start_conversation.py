from django.conf import settings
from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler

from app_prime_league.models import ScoutingWebsite, Team
from app_prime_league.teams import register_team
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


def just_wait_a_moment(chat_id, context: CallbackContext):
    context.bot.send_message(
        text="Alles klar, ich schaue, was ich dazu finden kann.\nDas dauert circa 40 Sekunden... ⏳\n",
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN,
    )
    # context.bot.send_message(
    #     text="Der Bot ist zurzeit deaktiviert, da er keine Updates mehr von der Prime League erhält.",
    #     chat_id=chat_id,
    #     parse_mode=ParseMode.MARKDOWN,
    # )


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
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
        return ConversationHandler.END
    if get_existing_chat_id(update) is not None:
        update.message.reply_markdown(
            text=(
                "In diesem Chat ist bereits ein Team registriert. "
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
                "Bitte versuche es erneut oder /cancel."
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
    chat_id = get_chat_id(update)
    just_wait_a_moment(chat_id, context)

    if team_is_locked(team_id):
        update.message.reply_markdown(
            text=(
                "Das Team *{team_name}* wurde bereits in einem anderen Chat registriert.\n"
                "Lösche zuerst die Verknüpfung im anderen Chat mit /delete. \n\n"
                "Solltest Du Hilfe benötigen, benutze /help."
            ).format(team_name=Team.objects.get_team(team_id).name),
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
        return 1

    if new_team is None and old_team is not None:
        old_team.telegram_id = old_team_chat_id
        old_team.save()
        update.message.reply_markdown(
            text=(
                "Die ID: *{id}* konnte *keinem* Team zugeordnet werden.\n\n"
                "Bitte kopiere deine *TEAM_URL* oder deine *TEAM_ID* in den Chat. Benutze /cancel um abzubrechen."
            ).format(id=team_id),
            disable_web_page_preview=True,
            quote=False,
        )
        return 1
    elif new_team is None:
        update.message.reply_markdown(
            text=(
                "Die ID: *{id}* konnte *keinem* Team zugeordnet werden.\n\n"
                "Bitte kopiere deine *TEAM_URL* oder deine *TEAM_ID* in den Chat. Benutze /cancel um abzubrechen."
            ).format(id=team_id),
            disable_web_page_preview=True,
        )
        return 1
    else:
        if new_team_old_chat_id is not None:
            update.message.reply_markdown(
                msg=(
                    "Dein Team wurde in einem anderen Chat registriert!\n"
                    "Es werden in dieser Gruppe keine weiteren Updates zu *{team.name}* folgen.\n\n"
                    "Solltest Du Hilfe benötigen, benutze /help."
                ).format(team=new_team),
                chat_id=new_team_old_chat_id,
                quote=False,
            )
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
    url = Team.objects.get(telegram_id=chat_id).logo_url
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
    team = Team.objects.get(telegram_id=chat_id)
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
        ).format(team_name=team.name, scouting_website=ScoutingWebsite.default().name),
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )

    msg = MatchesOverview(team=team)
    context.bot.send_message(
        text=msg.generate_message(),
        chat_id=chat_id,
        disable_web_page_preview=True,
        parse_mode=ParseMode.MARKDOWN,
    )
