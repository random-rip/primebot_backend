from django.core.management import BaseCommand

from app_api.modules.status.views import GitHub
from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage

message = """
Hallo {team.name},

🔥 Version {version} ist draußen 🔥

1️⃣ Implementierung einer eigenen API für euch. Aktuell sind Teams und Matches (inklusive Spieler) implementiert. Die API Dokumentation findet ihr unter https://github.com/random-rip/primebot_backend/blob/master/openapi.yml .
Gebt uns gerne Feedback dazu, was ihr davon haltet und was für Daten ihr noch gerne möchtet.
2️⃣ Einige kleine Fehler wurden behoben, wie beispielsweise dass nicht jeder `/match MATCH_DAY` funktioniert hat.

Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/changelogs

Sternige Grüße
– PrimeBot devs
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        teams = Team.objects.get_registered_teams().filter()
        for team in teams:
            try:
                print(team)
                dispatcher = MessageDispatcher(team)
                dispatcher.dispatch_raw_message(
                    msg=NotificationToTeamMessage(
                        team=team,
                        custom_message=message,
                        version=GitHub.latest_version()["version"],
                    )
                )
            except Exception as e:
                print(e)
