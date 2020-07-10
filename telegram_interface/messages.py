# Variablen
from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_FIGHT, EMOJI_CLOVER, EMOJI_MINDBLOWN, \
    EMOJI_POST_HORN

SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"
CANCEL = "/cancel"
BOOLEAN_KEYBOARD = [[YES], [NO], [SKIP, CANCEL, ]]
SETTINGS_FINISHED = "Einstellungen wurden gespeichert"
REGISTRATION_FINISH = "Perfekt! Du erhältst jetzt Updates von "
CANCEL = "Vorgang abgebrochen, leider. \n" \
         "Brauchst du Hilfe nutze /help"

GENERAL_MATCH_LINK = "https://www.primeleague.gg/de/leagues/matches/"
GENERAL_TEAM_LINK = "https://www.primeleague.gg/de/leagues/teams/"

US = "uns"
FOR_GAME_DAY = "für [Spieltag] {}"
FROM = "von {}"


# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = "/issue - um zu Erfahren wie Ihr eine Störung melden könnt\n" \
                    "/start - um euer Team zu registieren\n" \
                    "/feedback - um uns euer Feedback mitzuteilen\n" \
                    "/settings - um die Einstellungen des Bots zu bearbeiten"

# Antwort auf /issue
ISSUE = f"Habt Ihr einen Fehler bemerkt? Bitte schreibt uns eine Nachricht in unserer " \
        f"[Support-Gruppe]({SUPPORT_GROUP_LINK}) (inkl. Screenshots,... /bop) "

# Antwort auf /feedback
FEEDBACK = f"Habt ihr Feedback? Hinterlasst uns gerne eine Nachricht in unserer [Support-Gruppe]({SUPPORT_GROUP_LINK})."

# Antwort, wenn /start Team_id oder tg_id bereits vergeben
TEAM_EXISTING = "Euer Team ist bereits registriert und mit einem anderen Chat verknüpft oder " \
                "für diesen Chat ist bereits ein anderes Team hinterlegt\n" \
                "oder eure eingegebene URL ist falsch.\n" \
                "Solltet ihr Hilfe benötigen, nutzt bitte /help oder /issue ."

TEAM_ID_VALID = "Euer registriertes Team:\n"

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "Ahoi, \n" \
              "du bist es Leid, jeden Tag mühselig auf der PrimeLeague-Seite nach neuen Updates zu suchen?\n" \
              f"Dann bin ich hier genau richtig! " \
              f"Mit mir bekommst du alle Updates als {EMOJI_POST_HORN}Pushnachricht in diesen Chat. {EMOJI_MINDBLOWN}\n" \
              f"Bitte kopiere zunächst deine Team-URL (Format: {GENERAL_TEAM_LINK}" \
              "<TEAM ID>-<TEAM NAME>) in den Chat. \n" \
              f"Wenn du Hilfe brauchst: \n{HELP_COMMAND_LIST}"

# Antwort auf /start, wenn man command in einem 1on1 Chat aufruft
START_CHAT = "Ahoi, \n" \
             f"{EMOJI_ONE}Erstelle einen Chat\n" \
             f"{EMOJI_TWO}klicke [hier]({START_LINK}) und lade den Bot in deine Gruppe ein\n" \
             f"{EMOJI_THREE}Personalisiere deine Einstellungen\n" \
             f"Viel Glück auf den Richtfeldern! {EMOJI_CLOVER}"

# Settings (ConversationHandler)
START_SETTINGS = "Settings: "
SETTINGS = [
    # 0 WEEKLY_OP_LINK
    {
        "name": "weekly_op_link",
        "text": "Möchtet ihr jede Woche eine neue Benachrichtigung für die kommende Spielwoche erhalten?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
    # 1 LINEUP_OP_LINK
    {
        "name": "lineup_op_link",
        "text": "Möchtet ihr benachrichtigt werden, wenn der Gegner ein neues Lineup aufgestellt hat?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
    # 2 SCHEDULING_SUGGESTION
    {
        "name": "scheduling_suggestion",
        "text": "Möchtet ihr über neue Zeitvorschläge des Gegners informiert werden?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
    # 3 SCHEDULING_CONFIRMATION
    {
        "name": "scheduling_confirmation",
        "text": "Möchtet ihr bei der Bestätigung eines Zeitvorschlags benachrichtigt werden?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
]

# Update Messages

NEW_TIME_SUGGESTION_PREFIX = "Neuer Zeitvorschlag von [{}]({}{}) für [Spieltag {}]({}{}):\n"

NEW_TIME_SUGGESTIONS_PREFIX = "Neue Zeitvorschläge von [{}]({}{}) für [Spieltag {}]({}{}):\n"

SCHEDULING_AUTO_CONFIRMATION_TEXT = "[{}]({}{}) hat für [Spieltag {}]({}{}) weder die vorgeschlagene Zeit angenommen," \
                                    "noch eine andere vorgeschlagen. Damit ist der Spieltermin\n" + \
                                    "{}{} bestätigt."
SCHEDULING_CONFIRMATION_TEXT = "Spielbestätigung von [{}]({}{}) für [Spieltag {}]({}{}):\n{}{}"

GAME_BEGIN_CHANGE_TEXT = "Ein Administrator hat eine neue Zeit für das Match gegen {} " \
                         "([Spieltag {}]({}{})) festgelegt:\n{}{}"

NEW_LINEUP_TEXT = "[{}]({}{}) ([Spieltag {}]({}{})) hat ein neues [Lineup]({}) aufgestellt. {}"

WEEKLY_UPDATE_TEXT = "{}[Spieltag {}]({}{}) gegen [{}]({}{}):\nHier ist der [OP.GG Link]({}) des Teams."


WAIT_A_MOMENT_TEXT = "Alles klar, ich schaue, was ich dazu finden kann.\nDas kann einen Moment dauern...⏳"
