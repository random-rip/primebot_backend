# Variablen
from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_CLOVER, EMOJI_MINDBLOWN, \
    EMOJI_POST_HORN, EMOJI_TROPHY, EMJOI_MAGN_GLASS, EMOJI_SUCCESS, EMOJI_ARROW_RIGHT

SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"
SETTINGS_FINISHED = "Alles klar, ich habe die Einstellungen gespeichert."
REGISTRATION_FINISH = "Perfekt! Ich sende euch jetzt Benachrichtigungen in diese Gruppe, " \
                      f"wenn es neue Updates zu kommenden Matches gibt. {EMOJI_TROPHY}\n" \
                      f"Benutzt /settings, um noch die Benachrichtigungseinstellungen zu personalisieren."
CANCEL = "Vorgang abgebrochen, leider. \n" \
         f"Brauchst du Hilfe nutze /help. {EMJOI_MAGN_GLASS}"
RETRY_TEXT = "Bitte versuche es erneut oder /cancel."

GENERAL_MATCH_LINK = "https://www.primeleague.gg/de/leagues/matches/"
GENERAL_TEAM_LINK = "https://www.primeleague.gg/de/leagues/teams/"

US = "uns"
FOR_GAME_DAY = "für [Spieltag] {}"
FROM = "von {}"

ENABLED = "aktiviert"
DISABLED = "deaktiviert"

# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = "/issue - um zu erfahren, wie Ihr eine Störung melden könnt\n" \
                    "/start - um euer Team zu registieren\n" \
                    "/feedback - um meinen Entwicklern euer Feedback mitzuteilen\n" \
                    "/settings - um die Einstellungen des Bots zu bearbeiten\n" \
                    "/cancel - um den aktuellen Prozess abzubrechen\n" \
                    "/explain - um eine Erklärung zu dem Bot zu lesen\n" \
 \
    # Antwort auf /issue
ISSUE = f"Habt Ihr einen Fehler bemerkt? Bitte schreibt den Entwicklern eine Nachricht in ihrer " \
        f"[Support-Gruppe]({SUPPORT_GROUP_LINK}) (inkl. Screenshots,... /bop) "

# Antwort auf /feedback
FEEDBACK = f"Habt Ihr Feedback? Hinterlasst den Entwicklern gerne eine Nachricht in folgender " \
           f"[Support-Gruppe]({SUPPORT_GROUP_LINK})."

# Antwort, wenn /start Team_id oder tg_id bereits vergeben
TEAM_EXISTING = "Dieses Team ist bereits registriert und mit einem anderen Chat verknüpft oder\n" \
                "für diesen Chat ist bereits ein anderes Team hinterlegt oder\n" \
                "die Team ID wurde nicht gefunden.\n" \
                f"Solltet ihr Hilfe benötigen, nutzt bitte /help oder /issue.\n{RETRY_TEXT}"

CHAT_EXISTING = "Für diesen Chat ist bereits ein Team registriert. Solltet ihr Hilfe benötigen nutzt bitte /help"

TEAM_ID_NOT_VALID_TEXT = "Die angegebene URL entspricht nicht dem richtigen Format. \n" \
                         "Achte auf das richtige Format oder gebe die Team ID ein.\n" \
                         f"{RETRY_TEXT}"
TEAM_ID_VALID = "Euer registriertes Team:\n"

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "_Hallo Beschwörer, \n" \
              "du bist es Leid, jeden Tag mühselig auf der PrimeLeague-Seite nach neuen Updates zu suchen?\n" \
              f"Dann bin ich hier genau richtig:\n" \
              f"__Ich schicke dir alle Updates der Seite als Pushbenachrichtigung{EMOJI_POST_HORN} " \
              f"in diesen Gruppen-Chat.___ {EMOJI_MINDBLOWN}\n\n" \
              f"{EMOJI_ONE} Bitte kopiere dafür deine Team-URL (Format: {GENERAL_TEAM_LINK}<TEAM ID>-<TEAM NAME>)" \
              "oder deine Team ID in den Chat.\n" \
 \
    # Antwort auf /start, wenn man command in einem 1on1 Chat aufruft
START_CHAT = "_Hallo Beschwörer,\ndu möchtest den PrimeBot für Pushbenachrichtigungen nutzen?_\n\n" \
             "Setup:\n" \
             f"{EMOJI_ONE} Erstelle einen Gruppen-Chat in Telegram.\n" \
             f"{EMOJI_TWO} Klicke [hier]({START_LINK}) und lade so den PrimeBot in deine Gruppe ein.\n" \
             f"{EMOJI_THREE} Personalisiere mit /settings deine Einstellungen.\n\n" \
             f"_Viel Glück auf den Richtfeldern!_ {EMOJI_CLOVER}"

# Settings (ConversationHandler)
START_SETTINGS = "Settings: "
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
    "text": "Hauptmenü:\nWählt eine Einstellung aus, die ihr anpassen möchtet",
}

SET_PHOTO_TEXT = f"_Soll ich das Teambild aus der PrimeLeague importieren?_\n(Dazu werden Adminrechte benötigt)"
PHOTO_SUCESS_TEXT = f"{EMOJI_SUCCESS}"
PHOTO_ERROR_TEXT = f"Bild konnte nicht gesetzt werden."
PHOTO_RETRY_TEXT = f"Profilbild konnte nicht geändert werden. Bitte stellt sicher, dass ich Administrator bin und " \
                   f"die Gruppen-Info ändern darf\n_Soll ich das Teambild aus der PrimeLeague importieren?_"

MESSAGE_NOT_PINED_TEXT = f"Die wöchentliche Nachricht konnte nicht angeheftet werden. Bitte stellt für das nächste Mal " \
                         f"sicher, dass ich Administrator bin oder ausreichend Rechte habe um Nachrichten anzuheften. " \
                         f"Falls ihr nicht möchtet, dass die wöchentliche Benachrichtigung angeheftet wird, " \
                         f"nutzt bitte /settings {EMOJI_ARROW_RIGHT} 'Wochenübersicht anheften' {EMOJI_ARROW_RIGHT} " \
                         f"'Deaktivieren'."

# Update Messages
OWN_NEW_TIME_SUGGESTION_TEXT = "Neuer Zeitvorschlag von uns für [Spieltag {}]({}{}). {}"
NEW_TIME_SUGGESTION_PREFIX = "Neuer Zeitvorschlag von [{}]({}{}) für [Spieltag {}]({}{}):\n"

NEW_TIME_SUGGESTIONS_PREFIX = "Neue Zeitvorschläge von [{}]({}{}) für [Spieltag {}]({}{}):\n"

SCHEDULING_AUTO_CONFIRMATION_TEXT = "[{}]({}{}) hat für [Spieltag {}]({}{}) weder die vorgeschlagene Zeit angenommen," \
                                    "noch eine andere vorgeschlagen. Damit ist folgender Spieltermin bestätigt\n" + \
                                    "{}{}"
SCHEDULING_CONFIRMATION_TEXT = "Spielbestätigung von [{}]({}{}) für [Spieltag {}]({}{}):\n{}{}"

GAME_BEGIN_CHANGE_TEXT = "Ein Administrator hat eine neue Zeit für das Match gegen [{}]({}{}) " \
                         "([Spieltag {}]({}{})) festgelegt:\n{}{}"

NEW_LINEUP_TEXT = "[{}]({}{}) ([Spieltag {}]({}{})) hat ein neues [Lineup]({}) aufgestellt. {}"

NEXT_GAME_TEXT = "Euer nächstes Spiel:\n"
WEEKLY_UPDATE_TEXT = "{}[Spieltag {}]({}{}) gegen [{}]({}{}):\nHier ist der [OP.GG Link]({}) des Teams."

WAIT_A_MOMENT_TEXT = "Alles klar, ich schaue, was ich dazu finden kann.\nDas kann einen Moment dauern...⏳"
NO_GROUP_CHAT = "Dieser Befehl kann nur in einer Telegram-Gruppe ausgeführt werden."
TEAM_NOT_IN_DB_TEXT = "Die Telegram-Gruppe wurde noch nicht initialisiert (/start)."

EXPLAIN_TEXT = "Dieser Bot ist nicht in Kooperation mit der PrimeLeague bzw. der Freaks4u Gaming GmbH entstanden " \
               "und hat damit keinen direkten Bezug zur PrimeLeague. " \
               "Dieser Bot wurde aufgrund von versäumten Matches entworfen und programmiert. " \
               "Der Bot wurde nach bestem Gewissen realisiert, und nach einer Testphase für andere Teams zur " \
               "Verfügung gestellt. Dennoch sind alle Angaben ohne Gewähr! " \
               "**Funktionsweise:** Nach der Registrierung des Teams wird über die noch nicht gespielten Spiele " \
               "iteriert und deren Website nach Änderungen abgesucht. Dies geschieht alle 30 Minuten. " \
               "Das bedeutet, dass Updates maximal 30 Minuten alt sein können. Das wöchentliche Update geschieht " \
               "einmal jeden Montag um 0Uhr nach Beginn des Splits bis zum Ende der Gruppenphase. " \
               "Die gespeicherten Teams werden einmal pro Tag um 0Uhr aktualisiert."

CLOSE = "Schließen"
CURRENTLY = "Derzeitig"


