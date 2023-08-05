from django.core.management import BaseCommand

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import NotificationToTeamMessage
from core.github import GitHub

message = """
Hallo {team.name},

🔥 Version {version} ist draußen 🔥

{body}

Alle weiteren Änderungen findet ihr auf unserer Website: https://www.primebot.me/information/changelog

Sternige Grüße
– PrimeBot devs
"""


class Command(BaseCommand):
    def handle(self, *args, **options):
        version = GitHub.latest_version()["version"]
        body = GitHub.latest_version()["body"]
        teams = Team.objects.get_registered_teams().filter()
        for team in teams:
            try:
                print(team)
                collector = MessageCollector(team)
                collector.dispatch(
                    msg_class=NotificationToTeamMessage,
                    custom_message=message,
                    version=version,
                    body=body,
                )
            except Exception as e:
                print(e)
