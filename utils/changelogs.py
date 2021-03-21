from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_ARROW_RIGHT, EMOJI_POST_HORN, EMOJI_PEACE, EMOJI_PARTY1, \
    EMOJI_PARTY2

CHANGELOGS = {
    1: {
        "version": "1.12.0-beta",
        "text":
"""
Hallo {team.name}, 
hier ein kurze Zusammenfassung der letzten Änderungen am PrimeBot.

*Updates ({version}):*"""
f"""
{EMOJI_ONE} /reassign : Dieses Kommando ist jetzt in /start integriert. Falls ihr also ein *anderes* Team für diesen Chat registrieren möchtet, führt /start aus. 
{EMOJI_TWO} Team-Sperre: Um ein Team in einem anderen Chat neu zu registrieren muss unter /settings {EMOJI_ARROW_RIGHT} Team-Sperre dein Team vorher freigegeben werden.

*Bugfixes:*
Ein Fehler wurde behoben, bei dem nicht angezeigt wurde, wenn eine Nachricht nicht angeheftet werden konnte.

*Coming Soon:*
{EMOJI_ONE} Pushnachrichten für neue Kommentare in ungespielten Matches
{EMOJI_TWO} Discord-Bot

Wenn ihr keine Patchnotes erhalten wollt, deaktiviert die Einstellung in /settings {EMOJI_ARROW_RIGHT} Bot Patches.

Sternige Grüße
@Grayknife und @OrbisK
"""
    },
    2: {
        "version": "1.12.1-beta",
        "text": f"Supergroup Hotfix"
    },
    3: {
        "version": "1.12.2-beta",
        "text": f"My SQL Has Gone Away Hotfix"
    },
    4: {
        "version": "1.12.3-beta",
        "text": f"Ein Fehler wurde behoben, in dem nicht alle Teams die wöchentliche Benachrichtigung bekommen haben, "
                f"obwohl sie es aktiviert hatten."
    },
    5: {
        "version": "1.13.0-beta",
        "text":
"""
Hallo {team.name}, 
"""
f"""
der Spring Split 2021 steht in den Startlöchern und der Primebot ist natürlich wieder am Start!
Aufgrund der erhöhten Anzahl an Teams, die den Bot jetzt benutzen, kam es in den letzten Tagen leider zu einigen Ausfällen.
Jedes Team, welches diese Nachricht erhält, ist auf jeden Fall erfolgreich in der Datenbank hinterlegt worden. Bei Problemen oder Fragen benutzt /issue.
Allerdings können erst ab dem 29.01.2021 Benachrichtigungen{EMOJI_POST_HORN} bei Terminvorschlägen (o.ä.) gesendet werden.
Wir arbeiten außerdem daran, dass ihr mehr Informationen aus unserer Datenbank abfragen könnt. {EMOJI_PEACE}

Viel Erfolg im Split und sternige Grüße
Grayknife und Orbis
"""
    },
    6: {
        "version": "1.13.1-beta",
        "text": "Ein Fehler wurde behoben, bei dem Teams eine falsche Spieltag-Benachrichtigung bekommen haben."
    },
    7: {
        "version": "1.13.2-beta",
        "text": "Matches, in denen die Zeit von einem Administrator manuell eingestellt wurde, werden nun korrekt im System gespeichert und es werden nicht mehr mehrere Benachrichtigungen dazu gesendet."
    },
    8: {
        "version": "1.14.0-beta",
        "text":
"""
Hallo {team.name}, 
hier ein kurze Zusammenfassung der Neuerungen am PrimeBot.

*Updates ({version}):*"""
f"""
{EMOJI_ONE} Der Primebot steht jetzt auch auf *Discord* zur Verfügung! {EMOJI_PARTY2} Wir möchten die letzten beiden Spieltage nutzen, mögliche Fehler bei dieser Integration zu finden und das im Rahmen einer Closed Beta. Wenn ihr also Interesse habt, schreibt uns gerne privat (@Grayknife oder @OrbisK), damit wir euch whitelisten können.

*Bugfixes:*
Ein Fehler wurde behoben, bei dem Teams eine falsche Spieltag-Benachrichtigung bekommen haben.
Matches, in denen die Zeit von einem Administrator manuell eingestellt wurde, werden nun korrekt im System gespeichert und es werden nicht mehr mehrere Benachrichtigungen dazu gesendet.

*Coming Soon:*
{EMOJI_ONE} Pushnachrichten für neue Kommentare in ungespielten Matches

Ein Hinweis für Teams aus dem *Swiss Starter*: Aufgrund der unregelmäßigen Veröffentlichung der wöhentlich neuen Matches ist es für uns nur begrenzt möglich, euch zeitnah Updates für diese Matches zu benachrichtigen. Wir arbeiten für den nächsten Split an einer Lösung.

Wenn ihr keine Patchnotes erhalten wollt, deaktiviert die Einstellung in /settings {EMOJI_ARROW_RIGHT} Bot Patches.

Sternige Grüße
Grayknife und Orbis
"""
    },
    9: {
        "version": "1.14.1-beta",
        "text": "Matches, in denen denen eigene Lobbies erstellt wurden, werden nun beim Crawling berücksichtigt."
    },
}
