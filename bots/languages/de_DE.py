"""
EMOJI_ONE = "1️⃣"
EMOJI_TWO = "2️⃣"
EMOJI_THREE = "3️⃣"
EMOJI_ARROW = "⚡"
EMOJI_SUCCESS = "✅"
EMOJI_SAD = "😔"
EMOJI_FIGHT = "⚔"
EMOJI_TROPHY = "🏆"
EMJOI_MAGN_GLASS = "🔍"
EMOJI_LINEUP = "📈🆙"
EMOJI_SOON = "🔜"
EMOJI_CLOVER = "🍀"
EMOJI_MINDBLOWN = "🤯"
EMOJI_POST_HORN = "📯"
EMOJI_ARROW_RIGHT = "➡"
EMOJI_GIFT = "🎁"
EMOJI_PEACE = "✌"
EMOJI_FIRE = "🔥"
EMOJI_PARTY1 = "🥳"
EMOJI_PARTY2 = "🎉"
EMOJI_CALENDAR = "📆"
EMOJI_PIN = "📌"
EMOJI_BOOKMARK = "📑"
"""

SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
PRIME_LEAGUE_FORUM_LINK = "https://www.primeleague.gg/de/forums/1418-league-of-legends/1469-off-topic/637268"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"

REGISTRATION_FINISH = (
    "Perfekt! Ich sende dir jetzt Benachrichtigungen in diese Gruppe, "
    "wenn es neue Updates zu kommenden Matches gibt. 🏆\n"
    "Du kannst noch mit /settings Benachrichtigungen personalisieren und die Scouting Website (Standard: op.gg) ändern."
)
CANCEL = (
    "Vorgang abgebrochen. \n"
    "Wenn Du Hilfe brauchst, benutze /help. 🔍"
)
RETRY_TEXT = "Bitte versuche es erneut oder /cancel."

IT_REMAINS_AS_IT_IS = "Okay, es bleibt alles so, wie es ist."

ENABLED = "aktiviert"
DISABLED = "deaktiviert"

# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = (
    "/start - um dein Team zu registrieren\n"
    "/settings - um die Einstellungen fürs Team zu bearbeiten\n"
    "/matches - um eine Übersicht der offenen Matches zu erhalten\n"
    "/delete - um das registrierte Team zu entfernen\n"
    "/bop - What's boppin'?\n"
    "/cancel - um den aktuellen Vorgang abzubrechen\n"
    "/set_logo - um ein neues Logo aus der PrimeLeague zu holen\n"
)


NEED_HELP = "Solltest Du Hilfe benötigen, benutze /help."

CHAT_EXISTING = (
    "In diesem Chat ist bereits ein Team registriert. Möchtest Du ein anderes Team für diesen Channel registrieren?\n"
    f"Dann gib jetzt deine *Team-URL* oder deine *Team ID* an. Wenn nicht, benutze /cancel.\n\n"
    f"{NEED_HELP}"
)

TEAM_ID_NOT_VALID_TEXT = (
    "Die angegebene URL entspricht nicht dem richtigen Format.\n"
    "Achte auf das richtige Format oder gib die *Team ID* ein.\n"
    f"{RETRY_TEXT}"
)

TEAM_ID_VALID = "Dein registriertes Team:\n"

TEAM_ID_NOT_CORRECT = (
    "Die ID: *{id}* konnte *keinem* Team zugeordnet werden.\n\n"
    "Bitte kopiere deine *TEAM_URL* oder deine *TEAM_ID* in den Chat. Zum Abbrechen, benutze /cancel."
)

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = (
    "Sternige Grüße,\n"
    "Du bist es Leid, jeden Tag auf den Prime League-Seiten mühsam nach neuen Updates zu suchen?\n"
    "Gut, dass ich hier bin: Ich werde dich zu allen Änderungen bei euren Spielen updaten. 📯\n\n"
    "Bitte kopiere dafür deine *TEAM_URL* oder deine *TEAM_ID* in den Chat."
)

TEAM_LOCKED = (
    "Das Team *{team.name}* wurde bereits in einem anderen Chat registriert.\n"
    "Lösche zuerst die Verknüpfung im anderen Chat mit /delete. \n\n"
    f"{NEED_HELP}"
)

GROUP_REASSIGNED = (
    "Dein Team wurde in einem anderen Chat registriert!\n"
    "Es werden in dieser Gruppe keine weiteren Updates zu *{team.name}* folgen.\n\n"
    f"{NEED_HELP}"
)

# Antwort auf /start, wenn man command in einem 1on1 Chat aufruft
START_CHAT = (
    "Hallo,\n"
    "Du möchtest den PrimeBot für Pushbenachrichtigungen benutzen?\n\n"
    "Erste Scrhitte:\n"
    f"1️⃣ Erstelle einen Gruppen-Chat in Telegram und füge [mich]({START_LINK}) hinzu.\n"
    f"2️⃣ Registriere dein Team im Gruppenchat mit /start.\n"
    f"3️⃣ Personalisiere mit /settings deine Benachrichtigungen.\n\n"
    f"Viel Erfolg auf den Richtfeldern! 🍀"
)

# Settings (ConversationHandler)
MAIN_MENU_TEXT = "Hauptmenü"

BOOLEAN_KEYBOARD_OPTIONS = [
    {
        "title": "Aktivieren",
        "callback_data": "enable"
    },
    {
        "title": "Deaktivieren",
        "callback_data": "disable"
    },
    {
        "title": MAIN_MENU_TEXT,
        "callback_data": "main"
    },
]

SET_PHOTO_TEXT = (f"Soll ich das Teambild aus der Prime League importieren?\n"
                  f"_Dazu werden Adminrechte hier in der Gruppe benötigt._")
PHOTO_SUCCESS_TEXT = f"✅ Okay"
PHOTO_ERROR_TEXT = f"Bild konnte nicht gesetzt werden."
PHOTO_RETRY_TEXT = (
    f"Profilbild konnte nicht geändert werden. Soll ich das Teambild aus der Prime League importieren?\n"
    f"_Dazu werden Adminrechte benötigt._"
)


# Update Messages
OWN_NEW_TIME_SUGGESTION_TEXT = (
    "Neuer Terminvorschlag von euch für [Spieltag {match_day}]({match_url}). ✅"
)

SUGGESTIONS = (
    "von [{enemy_team_tag}]({enemy_team_url}) für [Spieltag {match_day}]({match_url}):\n"
)

NEW_TIME_SUGGESTION_PREFIX = "Neuer Terminvorschlag "
NEW_TIME_SUGGESTIONS_PREFIX = "Neue Terminvorschläge "

AUTOMATIC = "Automatische "
SCHEDULING_CONFIRMATION_TEXT = (
    "Spielbestätigung gegen [{enemy_team_tag}]({enemy_team_url}) für "
    "[Spieltag {match_day}]({match_url}):\n"
    "⚔{time}"
)

MATCH_BEGIN_CHANGE_TEXT = (
    "Ein Administrator hat eine neue Zeit für [Spieltag {match_day}]({match_url}) gegen "
    "[{enemy_team_tag}]({enemy_team_url}) festgelegt:\n"
    "⚔{time}"
)

NEW_LINEUP_TEXT = (
    "[{enemy_team_tag}]({enemy_team_url}) ([Spieltag {match_day}]({match_url})) hat ein neues "
    "[Lineup]({scouting_url}) aufgestellt. 📈🆙"
)

WEEKLY_UPDATE_TEXT = (
    "Der nächste Spieltag:\n"
    "🔜[Spieltag {match_day}]({match_url}) gegen [{enemy_team_tag}]({enemy_team_url}):\n"
    "Hier ist der [{website} Link]({scouting_url}) des Teams."
)

NEXT_MATCH_IN_CALIBRATION = (
    "Euer nächstes Spiel in der Kalibrierungsphase:\n"
    "🔜[Spiel {match_day}]({match_url}) gegen [{enemy_team_tag}]({enemy_team_url}):\n"
    "Hier ist der [{website} Link]({scouting_url}) des Teams."
)

WAIT_A_MOMENT_TEXT = "Alles klar, ich schaue, was ich dazu finden kann.\nDas kann einen Moment dauern...⏳\n"
NO_GROUP_CHAT = "Dieser Befehl kann nur in einer Telegram-Gruppe ausgeführt werden."
TEAM_NOT_IN_DB_TEXT = "In der Telegram-Gruppe wurde noch kein Team registriert (/start)."
TEAM_NOT_FOUND = "Dieses Team wurde noch nicht registriert (/start)."


TG_DELETE = (
    "Alles klar, ich habe alle Verknüpfungen zu dieser Gruppe und dem Team gelöscht. "
    f"Gebt uns gerne Feedback, falls euch Funktionalitäten fehlen oder nicht gefallen. Bye! ✌\n"
    f"_Das Team kann jetzt in einem anderen Channel registriert werden, "
    f"oder ein anderes Team kann in diesem Channel registriert werden._"
)

WEBSITE_LINK_TO_HELP = "https://primebot.me/crew/"
WEBSITE_LINK_TO_DISCORD = "https://primebot.me/discord"
CLOSE = "Schließen"
CURRENTLY = "Derzeitig"
PL_CONNECTION_ERROR = (
    "Momentan kann keine Verbindung zu der PrimeLeague Website hergestellt werden. "
    "Probiere es in ein paar Stunden noch einmal.\n"
    f"Wenn es später immer noch nicht funktioniert, schaue auf {WEBSITE_LINK_TO_HELP} nach Hilfe."
)
PL_TEAM_NOT_FOUND = (
    "Das Team wurde nicht auf der PrimeLeague Website gefunden. "
    "Stelle sicher, dass du das richtige Team registrierst."
)
DC_HELP_LINK_TEXT = f"Schaue auf unserer {WEBSITE_LINK_TO_DISCORD} nach Hilfe."
DC_TEAM_ID_NOT_VALID = (
    "Aus dem Übergabeparameter konnte keine ID gefunden werden "
    f"(Format `!start TEAM_ID_or_TEAM_URL`). {DC_HELP_LINK_TEXT}"
)
DC_CHANNEL_IN_USE = (
    "Für diesen Channel ist bereits ein Team registriert. Falls du hier ein anderes Team "
    "registrieren möchtest, lösche zuerst die Verknüpfung zum aktuellen Team mit `!delete`."
)
DC_TEAM_IN_USE = (
    "Dieses Team ist bereits in einem anderen Channel registriert. "
    f"Lösche zuerst die Verknüpfung im anderen Channel mit `!delete`. {DC_HELP_LINK_TEXT}"
)
DC_NO_PERMISSIONS_FOR_WEBHOOK = (
    "Mir fehlt die Berechtigung, Webhooks zu verwalten. Bitte stelle sicher, dass ich diese Berechtigung habe. "
    "Gegebenenfalls warte eine Stunde, bevor du den Befehl wieder ausführst. "
    f"Falls es danach noch nicht gehen sollte, schaue auf {WEBSITE_LINK_TO_DISCORD} nach Hilfe."
)
DC_REGISTRATION_FINISH = (
    "Perfekt, dieser Channel wurde für Team **{team_name}** registriert.\n"
    "Die wichtigsten Befehle:\n"
    "📌 `!role ROLE_NAME` - um eine Rolle zu setzen, die bei Benachrichtigungen erwähnt werden soll\n"
    "📌 `!settings` - um die Benachrichtigungen zu personalisieren oder die Scouting Website (Standard: op.gg) zu ändern\n"
    "📌 `!matches` - um eine Übersicht der noch offenen Matches zu erhalten\n"
    "📌 `!match MATCH_DAY` - um detaillierte Informationen zu einem Spieltag zu erhalten\n\n"
    "Einfach ausprobieren! 🎁 Der Status der Prime League API kann jederzeit auf https://primebot.me/ "
    "angeschaut werden. Dort findet ihr auch weitere Informationen zu den Befehlen."
)

DC_USE_FIX = (
    "Wenn keine Benachrichtigungen mehr in dem Channel ankommen, aber du das Team bereits registriert hast, "
    "benutze bitte `!fix`."
)

DC_WEBHOOK_RECREATED = (
    "Webhook wurde neu erstellt. Sollten weiterhin Probleme auftreten, schaue auf unserer "
    f"{WEBSITE_LINK_TO_DISCORD} > Probleme nach Hilfe."
)
DC_CHANNEL_NOT_INITIALIZED = (
    "In diesem Channel ist derzeitig kein Team registriert. Benutze dafür `!start TEAM_ID_oder_TEAM_URL`"
)
DC_ROLE_MENTION_REMOVED = (
    "Alles klar, ich habe die Rollenerwähnung entfernt. "
    "Du kannst sie bei Bedarf wieder einschalten, benutze dazu einfach `!role ROLE_NAME`."
)
DC_ROLE_NOT_FOUND = "Die Rolle {role_name} habe ich nicht gefunden. Stelle sicher, dass diese Rolle existiert."

DC_SET_ROLE = "Okay, ich informiere die Rolle **@{role_name}** ab jetzt bei neuen Benachrichtigungen. 📯"

DC_HELP_TEXT_START = "Registriert das Team im Channel (Beispiel: !start 105959)"
DC_HELP_TEXT_FIX = "Erstellt den Benachrichtigungswebhook neu"
DC_HELP_TEXT_ROLE = (
    "Setze eine Discordrolle, die in den Benachrichtigungen benutzt wird. Um die Rolle zu entfernen schreibe !role "
    "ohne Parameter"
)
DC_HELP_TEXT_OVERVIEW = "Erstellt eine Übersicht für die offenen Spiele"
DC_HELP_TEXT_SETTINGS = "Erstellt einen temporären Link um Benachrichtigungseinstellungen vorzunehmen"
DC_HELP_TEXT_BOP = "What's boppin'?"
DC_HELP_TEXT_MATCH = (
    "Erstellt eine Übersicht für den übergebenen Spieltag (Beispiel: !match 1)"
)
DC_HELP_TEXT_DELETE = (
    "Löscht die Channelverknüpfungen zum Team. Achtung, danach werden keine weiteren Benachrichtigungen gesendet."
)
DC_DESCRIPTION = (
    "Dieser Bot ist nicht in Kooperation mit der Prime League bzw. der Freaks4u Gaming GmbH entstanden und hat damit "
    "keinen direkten Bezug zur Prime League. Dieser Bot wurde aufgrund von versäumten Matches entworfen und "
    "programmiert. Der Bot wurde nach bestem Gewissen realisiert, und nach einer Testphase für andere Teams zur "
    "Verfügung gestellt. Dennoch sind alle Angaben ohne Gewähr! _Version: {version}_"
)

DC_DELETE = "Alles klar ich lösche alle Verknüpfungen zu diesem Channel und dem Team."

DC_BYE = (
    "Alles gelöscht. Gebt uns gerne Feedback auf https://discord.gg/K8bYxJMDzu, falls euch Funktionalitäten fehlen "
    "oder nicht gefallen. Bye! ✌\n"
    "_Das Team kann jetzt in einem anderen Channel registriert werden, oder ein anderes Team kann in diesem Channel "
    "registriert werden._"
)
TITLE_NEW_MATCH_DAY = "Wochenübersicht"
TITLE_NEW_MATCH = "Neues Spiel"
TITLE_NEW_LINEUP = "Neues Lineup"
TITLE_NEW_OWN_SUGGESTION = "Eigener neuer Terminvorschlag"
TITLE_NEW_SUGGESTION = "Neuer Terminvorschlag eines Gegners"
TITLE_MATCH_CONFIRMATION = "Terminbestätigung"

NO_CURRENT_MATCHES = "Ihr habt aktuell keine offenen Spiele."
OVERVIEW = "Eine Übersicht eurer offenen Spiele:"
MATCH_DAY = "Spieltag"
TIEBREAKER = "Tiebreaker"
CURRENT_LINEUP = "Aktuelles Lineup"
VS = "vs."

SETTINGS_CHANGE_TITLE = "Einstellungen für {team} ändern"
SETTINGS_TEMP_LINK = "Der Link ist nur {minutes} Minuten gültig. Danach muss ein neuer Link generiert werden."

OVERVIEW_DEPRECATED = "Der Befehl ist veraltet, bitte benutze `!matches` (Telegram: `/matches`)."

MATCH_DAY_NOT_VALID = (
    "Dieser Spieltag wurde nicht gefunden gefunden. Probiere es mit `!match 1`."
)
