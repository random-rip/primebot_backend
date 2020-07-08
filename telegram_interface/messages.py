FEEDBACK_MAIL = "COMING SOON"

# Start Message
HELP = "Hier ein kleiner Überblick: \n" \
       "/issue - um zu Erfahren wie Ihr eine Störung melden könnt\n" \
       "/start - um euer Team zu registieren\n" \
       "/feedback - um uns euer Feedback mitzuteilen"

START_GROUP = "Ahoi, \n" \
              "Hier könnte ein Sehr Kreativer Text Stehen... tut er aber nicht \n" + \
              HELP + \
              "Bitte Schreib zunächst deine Team-URL(Format: https://www.primeleague.gg/de/leagues/teams/" \
              "111111-XXXXX-XXXX-XXXXXXX) in den Chat, damit ich euch finden kann"

START_CHAT = "Ahoi, \n" \
             "1. Erstelle einen Chat\n" \
             "2. öffne https://t.me/prime_league_bot?startgroup=neu und lade den Bot in deine Gruppe ein\n" \
             "3. Beantworte die gestellten Fragen\n" \
             "Viel Spaß"

# Settings
START_SETTINGS = "Settings: "
# Option #1: Erhalt vom OP.GG Link

WEEKLY_OP_LINK_TEXT = "Möchtet Ihr jede Woche eine neue Benachrichtigung für die kommende Spielwoche erhalten?"

LINEUP_OP_LINK_TEXT = "Möchtest du benachrichtigt werden, wenn der Gegner ein neues Lineup aufgestellt hat?"

SCHEDULING_SUGGESTION_TEXT = "Möchtest du über neue Zeitvorschläge des Gegners informiert werden?"

SCHEDULING_CONFIRMATION_TEXT = "Möchtest du bei der Bestätigung eines Zeitvorschlags benachrichtigt werden?"

BOOLEAN_KEYBOARD = [["Ja"], ["Nein"]]

TEAM_EXISTING = "Dein Team ist bereits in registriert und mit einer anderen Gruppe verknüpft oder " \
                "für diese Gruppe ist bereits ein Team registriert\n" \
                "Oder die angegebene URL ist falsch. \n" \
                "Solltet ihr Hilfe benötigen, nutzt bitte /help oder /issue"

OPTION1 = "OP.GG Link: \n" \
          "Möchtet Ihr als Team einen OP.gg Link: \n" \
          "Komplettes Team - von jedem Spieler des Teams (solang noch kein Lineup feststeht). \n" \
          "Lineup - nur vom Lineup, sobald es feststeht oder sich ändert.\n" \
          "Beides - Komplettes Team und später vom Lineup \n" \
          "Keinen - Keinen OP.gg Link"

OPTION1_AUSWAHL = [["LineUp", "Komplettes Team"], ["Beides", "Keinen"]]

# Option #2: Termin-Vorschläge
OPTION2 = "Termin-Vorschläge: \n" \
          "Welche Updates zu Terminvorschlägen möchte euer Team erhalten? \n" \
          "Gegner - Benachrichtigung, sobald die Gegner Termine Vorschlagen \n" \
          "Alle - Benachrichtigungen von Terminvorschlägen des Gegners und des eigenen Teams \n" \
          "Keine - Keine Benachrichtigungen bei neuen Terminvorschlägen"

OPTION2_AUSWAHL = [["Gegner"], ["Alle", "Keine"]]

# Option #3:Erinnerung zum Ready-Melden
OPTION3 = "Erinnerung vor Spielbeginn:\n" \
          "Möchte euer Team eine Benachrichtigung sobald man sich 'Ready' melden kann?"

OPTION3_AUSWAHL = [["Ja"], ["Nein"]]

ISSUE = "Habt Ihr einen Fehler bemerkt? Bitte schreibt uns gern ein Ticket (inkl. Screenshots,...) https://gitlab.com/Grayknife/prime_league_bot/-/issues"

FEEDBACK = "Habt ihr Feedback? Schreibt es uns gern eine Mail " + FEEDBACK_MAIL + " oder eröffnet ein Ticket https://gitlab.com/Grayknife/prime_league_bot/-/issues"
FINISH = "Einstellungen wurden gespeichert"
