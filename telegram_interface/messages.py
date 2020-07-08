# Variablen
SUPPORT_GROUP_LINK = "https://t.me/joinchat/IUH8NhsKTYUtFKaqQMWhKA"
START_LINK = "https://t.me/prime_league_bot?startgroup=start"
YES = "Ja"
NO = "Nein"
SKIP = "Überspringen"
CANCEL = "/cancel"
BOOLEAN_KEYBOARD = [[YES], [NO], [SKIP, CANCEL, ]]
FINISH = "Einstellungen wurden gespeichert"
CANCEL = "Vorgang abgebrochen, leider. \n" \
         "Brauchst du Hilfe nutze /help"

# Antworten:
# Antwort auf /help
HELP_TEXT = "Überblick:\n"
HELP_COMMAND_LIST = "/issue - um zu Erfahren wie Ihr eine Störung melden könnt\n" \
                    "/start - um euer Team zu registieren\n" \
                    "/feedback - um uns euer Feedback mitzuteilen\n" \
                    "/settings - um die Einstellungen des Bots zu bearbeiten"

# Antwort auf /issue
ISSUE = f"Habt Ihr einen Fehler bemerkt? Bitte schreibt uns gern eine Nachricht in unserer [Support-Gruppe]({SUPPORT_GROUP_LINK}) (inkl. Screenshots,...) "

# Antwort auf /feedback
FEEDBACK = f"Habt ihr Feedback? Schreibt es uns gern eine Nachricht in unserer [Support-Gruppe]({SUPPORT_GROUP_LINK})."

# Antwort, wenn /start Team_id oder tg_id bereits vergeben
TEAM_EXISTING = "Euer Team ist bereits in registriert und mit einer anderen Gruppe verknüpft oder " \
                "für diese Gruppe ist bereits ein Team registriert\n" \
                "oder die angegebene URL ist falsch. \n" \
                "Solltet ihr Hilfe benötigen, nutzt bitte /help oder /issue"

TEAM_ID_VALID = "Euer registriertes Team:"

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "Ahoi, \n" \
              "du bist es Leid, jeden Tag mühselig auf der PrimeLeague-Seite nach neuen Updates zu suchen?\n" \
              "Dann bin ich hier genau richtig! \n" \
              "Bitte kopiere zunächst deine Team-URL (Format: https://www.primeleague.gg/de/leagues/teams/" \
              "<TEAM ID>-<TEAM NAME>) in den Chat. \n" \
              f"Wenn du Hilfe brauchst: \n{HELP_COMMAND_LIST}"

# Antwort auf /start, wenn man command in einem 1on1 Chat aufruft
START_CHAT = "Ahoi, \n" \
             "1. Erstelle einen Chat\n" \
             f"2. klicke [hier]({START_LINK}) und lade den Bot in deine Gruppe ein\n" \
             "3. Beantworte die gestellten Fragen\n" \
             "Viel Spaß"

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
