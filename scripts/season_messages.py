from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage

season_end_message = """
Hallo {team.name}, 

die Gruppenphase des aktuellen PrimeLeague-Splits ist vorbei und damit geht der Primebot bis zum nächsten Split in eine kurze Pause.
Die Benachrichtigungen der Tiebreakerspiele befinden sich noch in der Betaphase, wir können also nicht garantieren, dass ihr 100% der Benachrichtigungen bekommt.
Schaut aus diesem Grund also ab und zu selbst auf die Webseite.

Wenn ihr uns noch kein Feedback gegeben habt, würden wir uns darüber freuen, sodass wir den Primebot weiter verbessern können.
🔥 [Link zum Feedback](https://feedback.primebot.me/) 🔥


Sternige Grüße
Grayknife und Orbis
"""

season_start_message = """
Hallo {team.name}, 

die Anmeldung für den [Winter Split 2021](https://www.primeleague.gg/de/leagues/prm/2126-summer-split-2021) hat begonnen, also let´s go!
Mit dem Primebot startet ihr perfekt in den kommenden Split, ohne dass ihr jemals wieder etwas verpasst. 😱

Sternige Grüße
Grayknife und Orbis

"""

message = """
Hallo {team.name}, 

der PrimeBot wurde auf Version v2.0.0 aktualisiert. 
Mit dieser Version kommen ein paar neue Features und Überarbeitungen des Cores auf das Produktivsystem.

Hauptänderungen:
- Anbindung der Prime League API
- Deployment unserer Website und Personalisierung von Benachrichtigungen mit `!settings` (Telegram `/settings`).
- Wichtig: Wir haben alle Benachrichtigungseinstellungen zurückgesetzt (ging nicht anders, sorry).
- Implementierung von `!match [match_day]` um eine detaillierte Übersicht des Spieltages zu generieren.
- ...noch vieles mehr! Alle Aktualisierungen findet ihr [hier](https://primebot.me/changelogs).

Außerdem freuen wir uns euch mitteilen zu dürfen, dass wir nun deutlich häufiger die Daten der Prime League abgreifen dürfen.

Wir wünschen euch viel Erfolg beim restlichen Split! 

Sternige Grüße
Grayknife, Orbis & Mörlin
"""


def main():
    teams = Team.objects.get_watched_teams()
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            msg = NotificationToTeamMessage(team=team, custom_message=message)
            dispatcher.dispatch_raw_message(msg=msg)
        except Exception as e:
            print(e)


# python manage.py runscript debug
def run():
    main()
