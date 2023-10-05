from django.core.management import BaseCommand

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import NotificationToTeamMessage

message = """
Hallo {team.name},

der PrimeBot ist wieder online. 🔥

In Anbetracht der Umstellung und der Komplexität des technischen Umfelds, in dem wir arbeiten, gab es leider einige unvorhergesehene Herausforderungen, die unser Team bewältigen musste.
Wir haben hart daran gearbeitet, sicherzustellen, dass alle Daten sicher und intakt bleiben, aber trotz unserer besten Bemühungen ist es bedauerlicherweise zu diesem Verlust gekommen.
Wir haben bereits umfangreiche interne Untersuchungen durchgeführt, um die genaue Ursache dieses Vorfalls zu ermitteln, und wir arbeiten mit Hochdruck daran, sicherzustellen, dass sich so etwas in Zukunft nicht wiederholt.
Wir werden alle erforderlichen Maßnahmen ergreifen, um unsere Systeme und Prozesse zu verbessern und die Zuverlässigkeit unseres Dienstes zu erhöhen.

TLDR: We fucked up, alle Botinteraktionen von gestern sind lost (/start, /settings, /delete).
Aus diesem Grund müssen die Befehle von gestern nochmal erneut ausgeführt werden.

PS: Der Befehl /settings und die Website sind gerade noch down, was aber bis morgen noch behoben wird.

Falls es in den nächsten Tagen noch Probleme geben sollte, meldet euch bitte bei uns im Support-Channel.
Wir wünschen euch viel Erfolg im Wintersplit. 🏆🧊

Sternige Grüße
PrimeBot Devs
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        teams = Team.objects.get_registered_teams()
        for team in teams:
            try:
                print(team)
                collector = MessageCollector(team)
                collector.dispatch(msg_class=NotificationToTeamMessage, custom_message=message)
            except Exception as e:
                print(e)
