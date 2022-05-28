from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage, MatchesOverview

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

die Befehle für Matches in der Kalibrierungsphase wurden aktiviert (`!matches` & `!match 3`) und Updates werden nun minütlich abgefragt.

Sternige Grüße
Grayknife, Orbis & Mörlin
"""


def main():
    teams = Team.objects.get_registered_teams().filter()
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            msg = NotificationToTeamMessage(team=team, custom_message=message)
            dispatcher.dispatch_raw_message(msg=msg)
            dispatcher.dispatch(MatchesOverview, )
        except Exception as e:
            print(e)


def run():
    main()
