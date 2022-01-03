# Variablen
from prime_league_bot import settings
from utils.emojis import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_CLOVER, EMOJI_POST_HORN, EMOJI_TROPHY, \
    EMJOI_MAGN_GLASS, EMOJI_SUCCESS, EMOJI_GIFT, EMOJI_SOON, EMOJI_LINEUP, EMOJI_FIGHT, EMOJI_PEACE

SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
PRIME_LEAGUE_FORUM_LINK = "https://www.primeleague.gg/de/forums/1418-league-of-legends/1469-off-topic/637268"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"
SETTINGS_FINISHED = "Alles klar, ich habe die Einstellungen gespeichert."
REGISTRATION_FINISH = "Perfekt! Ich sende dir jetzt Benachrichtigungen in diese Gruppe, " \
                      f"wenn es neue Updates zu kommenden Matches gibt. {EMOJI_TROPHY}\n" \
                      f"Du kannst noch mit /settings Benachrichtigungen personalisieren " \
                      f"und die Scouting Website (Standard: OP.GG) ändern."
CANCEL = "Vorgang abgebrochen. \n" \
         f"Wenn Du Hilfe brauchst, benutze /help. {EMJOI_MAGN_GLASS}"
RETRY_TEXT = "Bitte versuche es erneut oder /cancel."

IT_REMAINS_AS_IT_IS = "Okay, es bleibt alles so, wie es ist."
GENERAL_MATCH_LINK = settings.MATCH_URI
GENERAL_TEAM_LINK = settings.TEAM_URI

ENABLED = "aktiviert"
DISABLED = "deaktiviert"

# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = \
    "/start - um dein Team zu registrieren\n" \
    "/settings - um die Einstellungen fürs Team zu bearbeiten\n" \
    "/cancel - um den aktuellen Vorgang abzubrechen\n" \
    "/issue - um zu erfahren, wie Du eine Störung melden kannst\n" \
    "/feedback - um meinen Entwicklern dein Feedback mitzuteilen\n" \
    "/explain - um eine Erklärung zu dem Bot zu erhalten\n" \
 \
    # Antwort auf /issue
ISSUE = f"Hast Du einen Fehler bemerkt? Bitte schreibe den Entwicklern eine Nachricht in ihrer " \
        f"[Support-Gruppe]({SUPPORT_GROUP_LINK}) (am besten inklusive Screenshots o.ä. /bop) "

# Antwort auf /feedback
FEEDBACK = f"Hast Du Feedback? Hinterlasse den Entwicklern gerne eine Nachricht im " \
           f"[Prime League-Forenthread]({PRIME_LEAGUE_FORUM_LINK})."

NEED_HELP = "Solltest Du Hilfe benötigen, benutze /help."

CHAT_EXISTING = "In diesem Chat ist bereits ein Team registriert. Möchtest Du ein anderes Team für diesen Channel " \
                "registrieren?\n" \
                f"Dann gib jetzt deine *Team-URL* " \
                "oder deine *Team ID* an. Wenn nicht, benutze /cancel.\n\n" \
                f"{NEED_HELP}"

TEAM_ID_NOT_VALID_TEXT = "Die angegebene URL entspricht nicht dem richtigen Format. \n" \
                         "Achte auf das richtige Format oder gib die *Team ID* ein.\n" \
                         f"{RETRY_TEXT}"
TEAM_ID_VALID = "Dein registriertes Team:\n"

TEAM_ID_NOT_CORRECT = "Die ID: *{id}* konnte *keinem* Team zugeordnet werden.\n\n" \
                      f"Bitte kopiere deine *TEAM_URL* " \
                      "oder deine *TEAM_ID* in den Chat. Zum Abbrechen, benutze /cancel."

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "Sternige Grüße, \n" \
              "Du bist es Leid, jeden Tag auf den Prime League-Seiten mühsam nach neuen Updates zu suchen?\n" \
              f"Gut, dass ich hier bin:\n" \
              f"Ich schicke dir alle *Updates* als *Pushbenachrichtigung* {EMOJI_POST_HORN} " \
              f"in diesen Chat. {EMOJI_GIFT}\n\n" \
              f"{EMOJI_ONE} Bitte kopiere dafür deine *TEAM_URL*" \
              " oder deine *TEAM_ID* in den Chat.\n"

TEAM_LOCKED = "Das Team *{team.name}* wurde bereits in einem anderen Chat registriert.\n" \
              f"Lösche zuerst die Verknüpfung im anderen Chat mit /delete. \n\n{NEED_HELP}"

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

SET_PHOTO_TEXT = f"Soll ich das Teambild aus der Prime League importieren?\n_Dazu werden Adminrechte hier in der Gruppe benötigt._"
PHOTO_SUCCESS_TEXT = f"{EMOJI_SUCCESS} Okay"
PHOTO_ERROR_TEXT = f"Bild konnte nicht gesetzt werden."
PHOTO_RETRY_TEXT = f"Profilbild konnte nicht geändert werden. Dazu werden Adminrechte benötigt.\n" \
                   f"_Soll ich das Teambild aus der Prime League importieren?_"

MESSAGE_NOT_PINNED_TEXT = f"Die wöchentliche Nachricht konnte nicht angeheftet werden. Dazu werden Adminrechte benötigt. " \
                          f"Falls Du nicht möchtest, dass die wöchentliche Benachrichtigung angeheftet wird, " \
                          f"deaktiviere in den /settings die Einstellung 'Wochenübersicht anheften'."

CANT_PIN_MSG_IN_PRIVATE_CHAT = "Man kann keine Nachricht in einem privaten Chat anpinnen."

# Update Messages
OWN_NEW_TIME_SUGGESTION_TEXT = "Neuer Zeitvorschlag von euch für [Spieltag {match_day}](" + \
                               GENERAL_MATCH_LINK + \
                               "{match_id})." + \
                               EMOJI_SUCCESS

NEW_TIME_SUGGESTION_PREFIX = "Neuer Zeitvorschlag von [{enemy_team_tag}](" + \
                             GENERAL_TEAM_LINK + \
                             "{enemy_team_id}) für [Spieltag {match_day}](" + \
                             GENERAL_MATCH_LINK + \
                             "{match_id}):\n"

NEW_TIME_SUGGESTIONS_PREFIX = "Neue Zeitvorschläge von [{enemy_team_tag}](" + \
                              GENERAL_TEAM_LINK + \
                              "{enemy_team_id}) für [Spieltag {match_day}](" + \
                              GENERAL_MATCH_LINK + \
                              "{match_id}):\n"

SCHEDULING_AUTO_CONFIRMATION_TEXT = "[{enemy_team_tag}](" + \
                                    GENERAL_TEAM_LINK + \
                                    "{enemy_team_id}) hat für [Spieltag {match_day}](" + \
                                    GENERAL_MATCH_LINK + \
                                    "{match_id}) weder die vorgeschlagene Zeit angenommen, " \
                                    "noch eine andere vorgeschlagen. Damit ist folgender Spieltermin bestätigt\n" + \
                                    EMOJI_FIGHT + "{time}"

SCHEDULING_CONFIRMATION_TEXT = "Spielbestätigung gegen [{enemy_team_tag}](" + \
                               GENERAL_TEAM_LINK + \
                               "{enemy_team_id}) für [Spieltag {match_day}](" + \
                               GENERAL_MATCH_LINK + \
                               "{match_id}):\n" + \
                               EMOJI_FIGHT + "{time}"

MATCH_BEGIN_CHANGE_TEXT = "Ein Administrator hat eine neue Zeit für das Match gegen [{enemy_team_tag}](" + \
                          GENERAL_TEAM_LINK + \
                          "{enemy_team_id}) " + \
                          "([Spieltag {match_day}](" + \
                          GENERAL_MATCH_LINK + \
                          "{match_id})) festgelegt:\n" + \
                          EMOJI_FIGHT + "{time}"

NEW_LINEUP_TEXT = "[{enemy_team_tag}](" + \
                  GENERAL_TEAM_LINK + \
                  "{enemy_team_id}) ([Spieltag {match_day}](" + \
                  GENERAL_MATCH_LINK + \
                  "{match_id})) hat ein neues [Lineup]({op_link}) aufgestellt. " + \
                  EMOJI_LINEUP

NEW_LINEUP_IN_CALIBRATION = "[{enemy_team_name}](" + \
                            GENERAL_TEAM_LINK + \
                            "{enemy_team_id}) hat für [Spiel {match_day}](" + \
                            GENERAL_MATCH_LINK + \
                            "{match_id}) ein neues [Lineup]({op_link}) aufgestellt. " + \
                            EMOJI_LINEUP

WEEKLY_UPDATE_TEXT = "Der nächste Spieltag:\n" + \
                     EMOJI_SOON + \
                     "[Spieltag {match_day}](" + \
                     GENERAL_MATCH_LINK + \
                     "{match_id}) gegen [{enemy_team_tag}](" + \
                     GENERAL_TEAM_LINK + \
                     "{enemy_team_id}):\n" + \
                     "Hier ist der [{website_name} Link]({op_link}) des Teams."

NEXT_MATCH_IN_CALIBRATION = "Euer nächstes Spiel in der Kalibrierungsphase:\n" + \
                            EMOJI_SOON + \
                            "[Spiel {match_day}](" + \
                            GENERAL_MATCH_LINK + \
                            "{match_id}) gegen [{enemy_team_tag}](" + \
                            GENERAL_TEAM_LINK + \
                            "{enemy_team_id}):\n" + \
                            "Hier ist der [{website_name} Link]({op_link}) des Teams."

WAIT_A_MOMENT_TEXT = "Alles klar, ich schaue, was ich dazu finden kann.\nDas kann einen Moment dauern...⏳\n"
NO_GROUP_CHAT = "Dieser Befehl kann nur in einer Telegram-Gruppe ausgeführt werden."
TEAM_NOT_IN_DB_TEXT = "In der Telegram-Gruppe wurde noch kein Team registriert (/start)."
TEAM_NOT_FOUND = "Dieses Team wurde noch nicht registriert (/start)."

EXPLAIN_TEXT = "Dieser Bot ist nicht in Kooperation mit der Prime League bzw. der Freaks4u Gaming GmbH entstanden " \
               "und hat damit keinen direkten Bezug zur Prime League. " \
               "Dieser Bot wurde aufgrund von versäumten Matches entworfen und programmiert. " \
               "Der Bot wurde nach bestem Gewissen realisiert, und nach einer Testphase für andere Teams zur " \
               "Verfügung gestellt. Dennoch sind alle Angaben ohne Gewähr!\n" \
               "\n_Version: {version}_"

TG_DELETE = "Alles klar, ich habe alle Verknüpfungen zu dieser Gruppe und dem Team gelöscht. " \
            f"Gebt uns gerne Feedback, falls euch Funktionalitäten fehlen oder nicht gefallen. Bye! {EMOJI_PEACE}\n" \
            f"_Das Team kann jetzt in einem anderen Channel registriert werden, oder ein anderes Team kann in diesem Channel registriert werden._"

WEBSITE_LINK_TO_HELP = "https://www.primebot.me/primebot-crew-kontakt/"
WEBSITE_LINK_TO_DISCORD = "https://www.primebot.me/start/f%C3%BCr-discord/"
CLOSE = "Schließen"
CURRENTLY = "Derzeitig"
PL_CONNECTION_ERROR = "Momentan kann keine Verbindung zu der PrimeLeague Website hergestellt werden. Probiere es in ein paar Stunden noch einmal.\n" \
                      f"Wenn es später immer noch nicht funktioniert, schaue auf {WEBSITE_LINK_TO_HELP} nach Hilfe."
PL_TEAM_NOT_FOUND = "Das Team wurde nicht auf der PrimeLeague Website gefunden. Stelle sicher, dass du das richtige Team initialisierst."
DC_HELP_LINK_TEXT = f"Schaue auf unserer {WEBSITE_LINK_TO_DISCORD} nach Hilfe."
DC_TEAM_ID_NOT_VALID = "Aus dem Übergabeparameter konnte keine ID gefunden werden " \
                       f"(Format `!start TEAM_ID_or_TEAM_URL`). {DC_HELP_LINK_TEXT}"
DC_CHANNEL_IN_USE = f"Für diesen Channel ist bereits ein Team registriert. Falls du hier ein anderes Team " \
                    f"registrieren möchtest, lösche zuerst die Verknüpfung zum aktuellen Team mit `!delete`."
DC_TEAM_IN_USE = f"Dieses Team ist bereits in einem anderen Channel registriert. " \
                 f"Lösche zuerst die Verknüpfung im anderen Channel mit /delete.{DC_HELP_LINK_TEXT}"
DC_NO_PERMISSIONS_FOR_WEBHOOK = "Mir fehlt die Berechtigung, Webhooks zu verwalten. " \
                                "Bitte stelle sicher, dass ich diese Berechtigung habe. " \
                                "Gegebenenfalls warte eine Stunde, bevor du den Befehl wieder ausführst. " \
                                "Falls es danach noch nicht gehen sollte, schaue auf " \
                                f"{WEBSITE_LINK_TO_DISCORD} nach Hilfe."
DC_REGISTRATION_FINISH = "Perfekt, dieser Channel wurde für Team {team_name} initialisiert.\n" \
                         "Wenn Du möchtest, kannst du mit `!role ROLE_NAME` noch eine Rolle benennen, " \
                         "die bei Benachrichtigungen erwähnt werden soll und mit `!settings` kannst du die " \
                         "Benachrichtigungen personalisieren oder die Scouting Website (Standard: OP.GG) ändern."
DC_USE_FIX = "Wenn keine Benachrichtigungen mehr in dem Channel ankommen, aber du das Team bereits registriert hast, " \
             "benutze bitte `!fix`."

DC_WEBHOOK_RECREATED = "Webhook wurde neu erstellt. Sollten weiterhin Probleme auftreten, schaue auf unserer " \
                       f"{WEBSITE_LINK_TO_DISCORD} > Probleme nach Hilfe."
DC_CHANNEL_NOT_INITIALIZED = "In diesem Channel ist derzeitig kein Team registriert. " \
                             "Benutze dafür `!start TEAM_ID_oder_TEAM_URL`"
DC_ROLE_MENTION_REMOVED = "Alles klar, ich habe die Rollenerwähnung entfernt. " \
                          "Du kannst sie bei Bedarf wieder einschalten, benutze dazu einfach `!role ROLE_NAME`."
DC_ROLE_NOT_FOUND = "Die Rolle {role_name} habe ich nicht gefunden. Stelle sicher, dass diese Rolle existiert."

DC_SET_ROLE = "Okay, ich informiere die Rolle **@{role_name}** ab jetzt bei neuen Benachrichtigungen. 📯"

DC_HELP_TEXT_START = "Registriere dein Team im Channel (Format: !start TEAM_ID_or_TEAM_URL)"
DC_HELP_TEXT_FIX = "Erstellt den Benachrichtigungswebhook neu"
DC_HELP_TEXT_ROLE = "Setze eine Discordrolle, die in den Benachrichtigungen benutzt wird. Um die Rolle zu entfernen schreibe !role ohne Parameter"
DC_HELP_TEXT_OVERVIEW = "Erstellt eine Übersicht für die offenen Spiele"
DC_HELP_TEXT_SETTINGS = "Erstellt einen temporären Link um Benachrichtigungseinstellungen vorzunehmen"
DC_HELP_TEXT_BOP = "Whats boppin'?"
DC_HELP_TEXT_DELETE = "Löscht die Channelverknüpfungen zum Team. Achtung, danach werden keine weiteren Benachrichtigungen gesendet."
DC_DESCRIPTION = "Dieser Bot ist nicht in Kooperation mit der Prime League bzw. der Freaks4u Gaming GmbH entstanden " \
                 "und hat damit keinen direkten Bezug zur Prime League. " \
                 "Dieser Bot wurde aufgrund von versäumten Matches entworfen und programmiert. " \
                 "Der Bot wurde nach bestem Gewissen realisiert, " \
                 "und nach einer Testphase für andere Teams zur Verfügung gestellt. " \
                 "Dennoch sind alle Angaben ohne Gewähr! _Version: {version}_"

DC_DELETE = "Alles klar ich lösche alle Verknüpfungen zu diesem Channel und dem Team."
DC_BYE = f"Alles gelöscht. Gebt uns gerne Feedback, falls euch Funktionalitäten fehlen oder nicht gefallen. Bye! {EMOJI_PEACE}\n" \
         f"_Das Team kann jetzt in einem anderen Channel registriert werden, oder ein anderes Team kann in diesem Channel registriert werden._"
TITLE_NEW_MATCH_DAY = "Neuer Spieltag"
TITLE_NEW_MATCH = "Neues Spiel"
TITLE_NEW_LINEUP = "Neues Lineup"
TITLE_NEW_OWN_SUGGESTION = "Eigener neuer Zeitvorschlag"
TITLE_NEW_SUGGESTION = "Neuer Zeitvorschlag eines Gegners"
TITLE_MATCH_CONFIRMATION = "Spielzeitbestätigung"

NO_CURRENT_MATCHES = "Ihr habt aktuell keine offenen Spiele."
OVERVIEW = "Eine Übersicht eurer offenen Spiele:"
MATCH_DAY = "Spieltag"
TIEBREAKER = "Tiebreaker"
CURRENT_LINEUP = "Aktuelles Lineup"
VS = "vs."

TG_SETTINGS_LINK = "[Einstellungen für {team} ändern]({link})\n" \
                   "_Der Link ist nur {minutes} Minuten gültig. Danach muss ein neuer Link generiert werden._"

SETTINGS_CHANGE_TITLE = "Einstellungen für {team} ändern"
SETTINGS_TEMP_LINK = "Der Link ist nur {minutes} Minuten gültig. Danach muss ein neuer Link generiert werden."
