# Variablen
from prime_league_bot import settings
from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_CLOVER, EMOJI_POST_HORN, EMOJI_TROPHY, \
    EMJOI_MAGN_GLASS, EMOJI_SUCCESS, EMOJI_ARROW_RIGHT, EMOJI_GIFT, EMOJI_SOON, EMOJI_LINEUP, EMOJI_FIGHT

SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
PRIME_LEAGUE_FORUM_LINK = "https://www.primeleague.gg/de/forums/1418-league-of-legends/1469-off-topic/637268-pl-spieltag-updates-als-push-benachrichtigung-aufs-handy"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"
SETTINGS_FINISHED = "Alles klar, ich habe die Einstellungen gespeichert."
REGISTRATION_FINISH = "Perfekt! Ich sende dir jetzt Benachrichtigungen in diese Gruppe, " \
                      f"wenn es neue Updates zu kommenden Matches gibt. {EMOJI_TROPHY}\n" \
                      f"Du kannst mit /settings deine Benachrichtigungen personalisieren."
CANCEL = "Vorgang abgebrochen. \n" \
         f"Wenn Du Hilfe brauchst, benutze /help. {EMJOI_MAGN_GLASS}"
RETRY_TEXT = "Bitte versuche es erneut oder /cancel."

GENERAL_MATCH_LINK = settings.MATCH_URI
GENERAL_TEAM_LINK = settings.TEAM_URI

ENABLED = "aktiviert"
DISABLED = "deaktiviert"

# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = \
    "/start - um dein Team zu registieren\n" \
    "/settings - um die Einstellungen des Benachrichtigungen zu bearbeiten\n" \
    "/cancel - um den aktuellen Vorgang abzubrechen\n" \
    "/issue - um zu erfahren, wie Du eine Störung melden kannst\n" \
    "/feedback - um meinen Entwicklern dein Feedback mitzuteilen\n" \
    "/explain - um eine Erklärung zu dem Bot zu erhalten\n" \
 \
    # Antwort auf /issue
ISSUE = f"Hast Du einen Fehler bemerkt? Bitte schreibe den Entwicklern eine Nachricht in ihrer " \
        f"[Support-Gruppe]({SUPPORT_GROUP_LINK}) (evtl. inklusive Screenshots,... /bop) "

# Antwort auf /feedback
FEEDBACK = f"Hast Du Feedback? Hinterlasse den Entwicklern gerne eine Nachricht im " \
           f"[Primeleague-Forenthread]({PRIME_LEAGUE_FORUM_LINK})."

NEED_HELP = "Solltest Du Hilfe benötigen, benutze /help."

# Antwort, wenn /start Team_id oder tg_id bereits vergeben
TEAM_EXISTING = "Dieses Team ist bereits registriert und mit einem anderen Chat verknüpft oder\n" \
                "für diesen Chat ist bereits ein anderes Team hinterlegt oder\n" \
                "die Team ID wurde nicht gefunden.\n" \
                f"Solltest Du Hilfe benötigen, benutze /help.\n{RETRY_TEXT}"

CHAT_EXISTING = "In diesem Chat ist bereits ein Team registriert. Möchtest Du ein anderes Team für diesen Channel " \
                "registrieren?\n" \
                f"Dann gib jetzt deine *Team-URL* (Format: {GENERAL_TEAM_LINK}<TEAM ID>-<TEAM NAME>)" \
                "oder deine *Team ID* an. Wenn nicht, benutze /cancel.\n\n" \
                f"{NEED_HELP}"

TEAM_ID_NOT_VALID_TEXT = "Die angegebene URL entspricht nicht dem richtigen Format. \n" \
                         "Achte auf das richtige Format oder gib die *Team ID* ein.\n" \
                         f"{RETRY_TEXT}"
TEAM_ID_VALID = "Dein registriertes Team:\n"

TEAM_ID_NOT_CORRECT = "Die ID: *{id}* konnte *keinem* Team zugeordnet werden.\n\n" \
                      f"Bitte kopiere deine Team-URL (Format: {GENERAL_TEAM_LINK}<TEAM ID>-<TEAM NAME>)" \
                      " oder die Team ID in den Chat. Zum Abbrechen, benutze /cancel."

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "Sternige Grüße, \n" \
              "Du bist es Leid, jeden Tag auf den PrimeLeague-Seiten mühsam nach neuen Updates zu suchen?\n" \
              f"Gut, dass ich hier bin:\n" \
              f"Ich schicke dir alle *Updates* als *Pushbenachrichtigung* {EMOJI_POST_HORN} " \
              f"in diesen Chat. {EMOJI_GIFT}\n\n" \
              f"{EMOJI_ONE} Bitte kopiere dafür deine Team-URL (Format: {GENERAL_TEAM_LINK}<TEAM ID>-<TEAM NAME>)" \
              " oder deine Team ID in den Chat.\n"

TEAM_LOCKED = "Das Team *{team.name}* wurde nicht freigegeben.\n" \
              "Bitte stelle sicher, dass in den Einstellungen von {team.name} die Team-Sperre *deaktiviert* ist!\n" \
              f"(/settings {EMOJI_ARROW_RIGHT} Team-Sperre)\n\n" \
              f"{NEED_HELP}"

GROUP_REASSIGNED = "Dein Team wurde in einem anderen Chat initialisiert!\n" \
                   "Es werden in dieser Gruppe keine weiteren Updates zu *{team.name}* folgen.\n\n" \
                   f"{NEED_HELP}"

# Antwort auf /start, wenn man command in einem 1on1 Chat aufruft


START_CHAT = "Hallo,\nDu möchtest den PrimeBot für Pushbenachrichtigungen benutzen?\n\n" \
             "Erste Scrhitte:\n" \
             f"{EMOJI_ONE} Erstelle einen Gruppen-Chat in Telegram und füge [mich]({START_LINK}) hinzu.\n" \
             f"{EMOJI_TWO} Registriere dein Team im Gruppenchat mit /start.\n" \
             f"{EMOJI_THREE} Personalisiere mit /settings deine Benachrichtigungen.\n\n" \
             f"Viel Erfolg auf den Richtfeldern! {EMOJI_CLOVER}"

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

SETTINGS_MAIN_MENU = {
    "text": "*Hauptmenü:*\nWelche Einstellung soll angepasst werden?",
}

SET_PHOTO_TEXT = f"Soll ich das Teambild aus der PrimeLeague importieren?\n_Dazu werden Adminrechte benötigt._"
PHOTO_SUCESS_TEXT = f"{EMOJI_SUCCESS}"
PHOTO_ERROR_TEXT = f"Bild konnte nicht gesetzt werden."
PHOTO_RETRY_TEXT = f"Profilbild konnte nicht geändert werden. Dazu werden Adminrechte benötigt.\n" \
                   f"_Soll ich das Teambild aus der PrimeLeague importieren?_"

MESSAGE_NOT_PINED_TEXT = f"Die wöchentliche Nachricht konnte nicht angeheftet werden. Dazu werden Adminrechte benötigt. " \
                         f"Falls Du nicht möchtest, dass die wöchentliche Benachrichtigung angeheftet wird, " \
                         f"benutze bitte /settings {EMOJI_ARROW_RIGHT} 'Wochenübersicht anheften' {EMOJI_ARROW_RIGHT} " \
                         f"'Deaktivieren'."

CANT_PIN_MSG_IN_PRIVATE_CHAT = "Man kann keine Nachricht in einem privaten Chat anpinnen."

# Update Messages
OWN_NEW_TIME_SUGGESTION_TEXT = "Neuer Zeitvorschlag von euch für [Spieltag {game_day}](" + \
                               GENERAL_MATCH_LINK + \
                               "{game_id})." + \
                               EMOJI_SUCCESS

NEW_TIME_SUGGESTION_PREFIX = "Neuer Zeitvorschlag von [{enemy_team_tag}](" + \
                             GENERAL_TEAM_LINK + \
                             "{enemy_team.id}) für [Spieltag {game_day}](" + \
                             GENERAL_MATCH_LINK + \
                             "{game_id}):\n"

NEW_TIME_SUGGESTIONS_PREFIX = "Neue Zeitvorschläge von [{enemy_team_tag}](" + \
                              GENERAL_TEAM_LINK + \
                              "{enemy_team_id}) für [Spieltag {game_day}](" + \
                              GENERAL_MATCH_LINK + \
                              "{game_id}):\n"

SCHEDULING_AUTO_CONFIRMATION_TEXT = "[{enemy_team_tag}](" + \
                                    GENERAL_TEAM_LINK + \
                                    "{enemy_team_id}) hat für [Spieltag {game_day}](" + \
                                    GENERAL_MATCH_LINK + \
                                    "{game_id}) weder die vorgeschlagene Zeit angenommen," \
                                    "noch eine andere vorgeschlagen. Damit ist folgender Spieltermin bestätigt\n" + \
                                    EMOJI_FIGHT + "{time}"

SCHEDULING_CONFIRMATION_TEXT = "Spielbestätigung von [{enemy_team_tag}](" + \
                               GENERAL_TEAM_LINK + \
                               "{enemy_team_id}) für [Spieltag {game_day}](" + \
                               GENERAL_MATCH_LINK + \
                               "{game_id}):\n" + \
                               EMOJI_FIGHT + "{time}"

GAME_BEGIN_CHANGE_TEXT = "Ein Administrator hat eine neue Zeit für das Match gegen [{enemy_team_tag}](" + \
                         GENERAL_TEAM_LINK + \
                         "{enemy_team_id}) " + \
                         "([Spieltag {game_day}](" + \
                         GENERAL_MATCH_LINK + \
                         "{game_id})) festgelegt:\n" + \
                         EMOJI_FIGHT + "{time}"

NEW_LINEUP_TEXT = "[{enemy_team_tag}](" + \
                  GENERAL_TEAM_LINK + \
                  "{enemy_team_id}) ([Spieltag {game_day}](" + \
                  GENERAL_MATCH_LINK + \
                  "{game_id})) hat ein neues [Lineup]({op_link}) aufgestellt. " + \
                  EMOJI_LINEUP

WEEKLY_UPDATE_TEXT = "Der nächste Spieltag:\n" + \
                     EMOJI_SOON + \
                     "[Spieltag {game_day}](" + \
                     GENERAL_MATCH_LINK + \
                     "{game_id}) gegen [{enemy_team_tag}](" + \
                     GENERAL_TEAM_LINK + \
                     "{enemy_team_id}):\n" + \
                     "Hier ist der [OP.GG Link]({op_link}) des Teams."

WAIT_A_MOMENT_TEXT = "Alles klar, ich schaue, was ich dazu finden kann.\nDas kann einen Moment dauern...⏳"
NO_GROUP_CHAT = "Dieser Befehl kann nur in einer Telegram-Gruppe ausgeführt werden."
TEAM_NOT_IN_DB_TEXT = "Die Telegram-Gruppe wurde noch nicht initialisiert (/start)."
TEAM_NOT_FOUND = "Dieses Team wurde noch nicht initialisiert (/start)."

EXPLAIN_TEXT = "Dieser Bot ist nicht in Kooperation mit der PrimeLeague bzw. der Freaks4u Gaming GmbH entstanden " \
               "und hat damit keinen direkten Bezug zur PrimeLeague. " \
               "Dieser Bot wurde aufgrund von versäumten Matches entworfen und programmiert. " \
               "Der Bot wurde nach bestem Gewissen realisiert, und nach einer Testphase für andere Teams zur " \
               "Verfügung gestellt. Dennoch sind alle Angaben ohne Gewähr!\n" \
               "*Funktionsweise:* Nach der Registrierung des Teams wird über die noch nicht gespielten Spiele " \
               "iteriert und deren Website nach Änderungen abgesucht. Dies geschieht alle 30 Minuten. " \
               "Das bedeutet, dass Updates maximal 30 Minuten alt sein können. Das wöchentliche Update geschieht " \
               "einmal jeden Montag um 0Uhr nach Beginn des Splits bis zum Ende der Gruppenphase. " \
               "Die gespeicherten Teams werden einmal pro Tag um 0Uhr aktualisiert. \n_Version: {version}_"

CLOSE = "Schließen"
CURRENTLY = "Derzeitig"
