from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage

season_end_message = """
Hallo {team.name}, 

die Gruppenphase des aktuellen PrimeLeague-Splits ist vorbei und damit geht der Primebot bis zum nächsten Split in eine kurze Pause.

Wenn ihr uns noch kein Feedback gegeben habt, würden wir uns darüber freuen, sodass wir den Primebot weiter verbessern können.
🔥 [Link zum Feedback](https://feedback.primebot.me/) 🔥


Sternige Grüße
Grayknife und Orbis
"""

season_start_message = """
Hallo {team.name}, 

die Anmeldung für den [Winter Split 2022](https://www.primeleague.gg/de/leagues/prm/2126-summer-split-2021) hat begonnen, also let´s go!
Mit dem PrimeBot startet ihr perfekt in den kommenden Split, ohne dass ihr jemals wieder etwas verpasst. 😱

Sternige Grüße
Grayknife und Orbis

"""

message = """
Hallo {team.name},

**für Discord**:
da Discord nach dem 31.8. API Versionen einstampft und Beschränkungen zu Daten erhöht (https://support-dev.discord.com/hc/en-us/articles/4404772028055), mussten wir zwangsweise die `discord.py` Version erhöhen.

Dadurch ergeben sich folgende Änderungen für euch:
1️⃣ Um mit dem PrimeBot in Zukunft zu kommunizieren, benötigt er weitere Berechtigungen (Slashbefehle). Dazu müsst ihr den Bot von eurem Server entfernen und neu hinzufügen (https://discord.com/api/oauth2/authorize?client_id=739550721703280700&permissions=2684472384&scope=bot).
2️⃣ Weil dadurch der Bot gekickt wurde, wurden alle Webhooks gelöscht. In jedem registrierten Channel muss deswegen `/fix` ausgeführt werden.
3️⃣ Ab sofort gibt es nur noch Slash-Befehle. Führt dazu am besten `/help` aus, um eine Übersicht aller Befehle anzuschauen.

Diese Schritte solltet ihr **unbedingt ausführen**, ansonsten funktioniert der PrimeBot für euer Team nicht mehr.

Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/changelogs

Sternige Grüße
Grayknife, Orbis & Mörlin
"""


def main():
    teams = Team.objects.get_registered_teams().filter()
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            dispatcher.dispatch_raw_message(msg=NotificationToTeamMessage(team=team, custom_message=message))
        except Exception as e:
            print(e)


def run():
    main()
