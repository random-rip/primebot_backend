from django.core.management import BaseCommand

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import NotificationToTeamMessage

message = """
Hallo {team.name},

aufgrund von Wartungsarbeiten ist der PrimeBot vorübergehend nicht erreichbar. Er sendet währenddessen auch keine Benachrichtigungen. Wir bitten um euer Verständnis.

PS: Der Wintersplit startet morgen. Ihr habt noch bis 23:59 Uhr Zeit euch zu registrieren.

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
