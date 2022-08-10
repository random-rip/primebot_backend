from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage, MatchesOverview

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

im folgenden möchten wir euch zwei Neuigkeiten mitteilen, an denen wir die letzten Wochen gearbeitet haben:

1️⃣ In den vergangenen Splits hat sich die Nachfrage des PrimeBots und neuer Features stark erhöht. Deswegen haben wir beschlossen den PrimeBot als OpenSource 🔥 bereitzustellen. 
Wenn ihr Ideen zu Features habt, neue Features implementieren wollt oder Bugs beheben möchtet, findet ihr alles weitere dazu auf [GitHub](https://github.com/random-rip/primebot_backend). Auch wenn ihr keine Programmierer:innen seid, wir sammeln auch Feedback zu Features, die in der Pipeline sind.

2️⃣ Da der PrimeBot dauerhaft kostenlos für alle sein soll, aber der Betrieb nicht kostenfrei bleibt, kooperieren wir ab sofort mit der [singularIT](https://www.singular-it.de/) 🏢. 
Wir drei arbeiten als Entwickler bei der singularIT und haben die Möglichkeit erhalten, Teile der Entwicklung am PrimeBot als SideProject-Time während unserer Arbeitszeit zu realisieren. Auch unterstützt uns die singularIT finanziell bei den Serverkosten.

Als Teil von singularIT deshalb an der Stelle ein kleiner Shoutout:
> Die singularIT ist ein Softwareunternehmen mit Schwerpunkt auf Webentwicklung (Frontend und Backend), Mobile Development und Data Analytics. 
> Wer Lust hat, Teil unseres [Teams](https://www.singular-it.de/team) zu werden und mit uns Projekte zu verwirklichen, ist sehr gerne eingeladen sich bei uns zu melden.

Wir freuen uns auf die gemeinsame Zukunft des PrimeBots!

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
