from app_prime_league.models import Team
from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import NotificationToTeamMessage

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

der Wintersplit beginnt bald und einigen Teams hat der PrimeBot bei der Kalibrierungsphase schon geholfen.
Heute wurden die Gruppen und die Spiele  erstellt, die ihr auf der Website schon einsehen könnt,  jedoch kommt es von unserer Seite aus momentan zu Fehlern bei der Datenabfrage. #wirsitzendran
Wir melden uns, sobald der PrimeBot wieder voll funktionsfähig ist. (vrstl. im Laufe des heutigen Abends)

Sternige Grüße
Grayknife und Orbis

"""


def main():
    teams = Team.objects.filter(id=105959) # _watched_team_of_current_split()
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            msg = NotificationToTeamMessage(team=team, custom_message=message)
            dispatcher.dispatch_raw_message(msg=msg)
        except Exception as e:
            print("ERROR", e)


# python manage.py runscript debug
def run():
    main()
