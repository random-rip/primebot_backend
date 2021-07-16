from utils.constants import EMOJI_ONE, EMOJI_TWO, EMOJI_ARROW_RIGHT, EMOJI_POST_HORN, EMOJI_PEACE, EMOJI_PARTY2

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
    10: {
        "version": "1.14.2-beta",
        "text":
            """
            Hallo {team.name}, 
            
            die Gruppenphase des aktuellen PrimeLeague-Splits ist vorbei und damit geht der Primebot bis zum nächsten Split in eine kurze Pause.
            Die Tiebreakerspiele, die diese Woche noch stattfinden, werden von unserem Bot (noch) *nicht* berücksichtigt.
            
            Wir sammeln in der Pause fleißig Feedback zum Bot, zu seinen Funktionalitäten und zur Discordintegration. 🏆
            Aus dem Grund freuen wir uns, wenn ihr uns Feedback in diesem [PL Forenpost](https://www.primeleague.gg/de/forums/1418-league-of-legends/1469-off-topic/637268) oder uns privat gebt.  
            
            Wir haben auf jeden Fall Bock neue geile Features zu entwickeln! 🔥
            
            Sternige Grüße
            Grayknife und Orbis
            """
    },
    11: {
        "version": "1.15-beta",
        "text":
            """
            Hallo {team.name}, 
            """
            f"""
die Anmeldung für den [Summer Split 2021](https://www.primeleague.gg/de/leagues/prm/2126-summer-split-2021) hat begonnen, also let´s go!
Mit dem Primebot startet ihr perfekt in den kommenden Split, ohne dass ihr jemals wieder etwas verpasst. 😱
Übrigens gibt es den Primebot jetzt auch als 🔥[Discord-Bot](https://discord.com/api/oauth2/authorize?client_id=***REMOVED***&permissions=536964096&scope=bot)🔥. Nachdem ihr den Bot zum Server hinzugefügt habt, gebt einfach in einem Channel eurer Wahl `!start <TEAM-LINK>` ein. Falls ihr Hilfe benötigt, schreibt uns gerne direkt an.

Sternige Grüße
Grayknife und Orbis

"""
    },
    12: {
        "version": "1.15.1-beta",
        "text":
            """
            Hallo {team.name}, 
            """
            f"""
neben einem Hotfix für den 🔥Discord-Bot🔥 gibt es jetzt auch für diesen die Möglichkeit eine Gruppe anzugeben, sodass diese bei Benachrichtungen erwähnt wird.
Das ganze kann auf Discord mit `!role <ROLE_NAME>` gesetzt werden.

Sternige Grüße
Grayknife und Orbis

"""
    },
    13: {
        "version": "1.15.2-beta",
        "text": "Add more Changelog logic"
    },
    14: {
        "version": "1.15.3-beta",
        "text": "Hotfix Logging error"
    },
    15: {
        "version": "1.16",
        "text":
            """
            Hallo {team.name}, 
            """
            f"""
wir haben Neuigkiten für euch:

1️⃣ Entschuldigt bitte, falls ihr in den letzten Tagen vermehrt Nachrichten zum Start der Gruppenphase mit einer **Übersicht aller Spiele** bekommen habt (oder auch gar keine bekommen habt).
Um jedem Team nochmal die Gelegenheit zu geben, eine korrekte Übersicht ihrer Spiele zu geben, haben wir den Befehl **!overview** (Discord) bzw. **/overview** (Telegram) hinzugefügt.

2️⃣ Der Primebot hat jetzt eine eigene [Website](https://www.primebot.me/)! Unter anderem findet ihr dort nochmal die ganzen Vorteile des Bots aufgelistet, wie man sein Team beim Bot registrieren kann, und mögliche Problemlösungen wenn der Bot nicht das tut, was man ihm sagt.
Falls euch der PrimeBot also gefällt und ihr andere Teams darauf aufmerksaam machen wollt, schickt ihnen einfach den Link zur Website. :)

3️⃣ Der Primebot hat mit der neuen Website auch ein neues Gesicht bekommen (eventuell habt ihr es schon bemerkt). 
Für die Teams auf Discord gilt: Um das neue Logo zu sehen, muss der Webhook neu erstellt werden. Gebt dazu einfach **!fix** in den Chat ein.

🔥Viel Erfolg in diesem Split!🔥
Sternige Grüße
Grayknife und Orbis
""",
    },
    16: {
        "version": "1.16.1",
        "text": "Ein Fehler wurde behoben, bei dem nicht alle Teams eine wöchentliche Benachrichtigung bekommen haben.",
    }
}
