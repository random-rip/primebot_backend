from django.core.management import BaseCommand

from app_prime_league.models import Team
from bots.message_dispatcher import MessageCollector
from bots.messages import NotificationToTeamMessage


class Command(BaseCommand):
    def handle(self, *args, **options):
        teams = Team.objects.get_registered_teams()
        pattern = """
        Hallo {team.name}, 

        der Split neigt sich dem Ende, und damit geht der PrimeBot in eine kurze Pause. Momentan sind noch Playoffs, dabei wünschen wir den teilnehmenden Teams viel Erfolg. 🏆

        Außerdem freuen uns über euer Feedback!
        Da wir bemüht sind den Primebot weiterhin zu verbessern, möchten wir in einem kurzen Feedback fragen, welche Features euch wirklich interessieren und welche Features euch noch fehlen.
        🔥[Link zum Feedback](https://feedback.primebot.me/)🔥

        Sternige Grüße
        Grayknife und Orbis
        """
        for team in teams:
            try:
                print(team)
                collector = MessageCollector(team)
                collector.dispatch(msg_class=NotificationToTeamMessage, custom_message=pattern)
            except Exception as e:
                print(e)
