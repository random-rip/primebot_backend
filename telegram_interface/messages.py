# Variablen
FEEDBACK_MAIL = "COMING SOON"
BOOLEAN_KEYBOARD = [["Ja"], ["Nein"], ["/cancel"]]
FINISH = "Einstellungen wurden gespeichert"

# Antworten:
# Antwort auf /help
HELP = "Hier ein kleiner Überblick: \n" \
       "/issue - um zu Erfahren wie Ihr eine Störung melden könnt\n" \
       "/start - um euer Team zu registieren\n" \
       "/feedback - um uns euer Feedback mitzuteilen"

# Antwort auf /issue
ISSUE = "Habt Ihr einen Fehler bemerkt? Bitte schreibt uns gern ein Ticket (inkl. Screenshots,...) https://gitlab.com/Grayknife/prime_league_bot/-/issues"

# Antwort auf /feedback
FEEDBACK = "Habt ihr Feedback? Schreibt es uns gern eine Mail " + FEEDBACK_MAIL + " oder eröffnet ein Ticket https://gitlab.com/Grayknife/prime_league_bot/-/issues"

# Antwort, wenn /start Team_id oder tg_id bereits vergeben
TEAM_EXISTING = "Dein Team ist bereits in registriert und mit einer anderen Gruppe verknüpft oder " \
                "für diese Gruppe ist bereits ein Team registriert\n" \
                "Oder die angegebene URL ist falsch. \n" \
                "Solltet ihr Hilfe benötigen, nutzt bitte /help oder /issue"

# Start Messages
# Antwort auf /start, wenn man command in einer Gruppe aufruft
START_GROUP = "Ahoi, \n" \
              "Hier könnte ein Sehr Kreativer Text Stehen... tut er aber nicht \n" + \
              HELP + \
              "Bitte Schreib zunächst deine Team-URL(Format: https://www.primeleague.gg/de/leagues/teams/" \
              "111111-XXXXX-XXXX-XXXXXXX) in den Chat, damit ich euch finden kann"

# Antwort auf /start, wenn man command in einem 1on1 Chat aufruft
START_CHAT = "Ahoi, \n" \
             "1. Erstelle einen Chat\n" \
             "2. öffne https://t.me/prime_league_bot?startgroup=neu und lade den Bot in deine Gruppe ein\n" \
             "3. Beantworte die gestellten Fragen\n" \
             "Viel Spaß"

# Settings (ConversationHandler)
START_SETTINGS = "Settings: "
SETTINGS = [
    # 0 WEEKLY_OP_LINK
    {
        "name": "weekly_lineup_op_link",
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
        "text": "Möchtest du über neue Zeitvorschläge des Gegners informiert werden?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
    # 3 SCHEDULING_CONFIRMATION
    {
        "name": "scheduling_confirmation",
        "text": "Möchtest du bei der Bestätigung eines Zeitvorschlags benachrichtigt werden?",
        "keyboard": BOOLEAN_KEYBOARD,
    },
]
