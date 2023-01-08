from django.core.management import BaseCommand

from app_api.modules.status.views import GitHub
from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import NotificationToTeamMessage

message = """
Hallo {team.name},

🔥 Version {version} ist draußen 🔥

1️⃣ Es wurde eine eigene API für euch veröffentlicht. Aktuell sind Teams und Matches (inklusive Spieler) implementiert. Die API Dokumentation findet ihr unter https://github.com/random-rip/primebot\_backend/blob/master/openapi.yml .
Gebt uns gerne Feedback dazu, was ihr davon haltet und was für Daten ihr noch gerne möchtet.
2️⃣ Benachrichtigungen werden nun mehrmals versucht zu senden, wenn diese aus Downtimegründen von Discord oder Telegram nicht bei euch ankommen.

Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/information/changelog

Sternige Grüße
– PrimeBot devs
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        version = GitHub.latest_version()["version"]
        teams = Team.objects.get_registered_teams().filter()
        for team in teams:
            try:
                print(team)
                collector = MessageCollector(team)
                collector.dispatch(
                    msg_class=NotificationToTeamMessage,
                    custom_message=message,
                    version=version,
                )
            except Exception as e:
                print(e)
