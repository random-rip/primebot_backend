from app_prime_league.models import Team
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NotificationToTeamMessage


def main():
    teams = Team.objects.get_watched_teams()
    pattern = """
Hallo {team.name}, 

die Gruppenphasen- und Tiebreakerspiele sind zuende, und damit geht der PrimeBot in die Winterpause. Momentan sind noch Playoffs, dabei wünschen wir den teilnehmenden Teams viel Erfolg. 🏆

Außerdem freuen uns über euer Feedback!
Da wir bemüht sind den Primebot weiterhin zu verbessern, möchten wir in einem kurzen Feedback fragen, welche Features euch wirklich interessieren und welche Features euch noch fehlen.
🔥[Link zum Feedback](http://feedback.primebot.me/)🔥

Sternige Grüße
Grayknife und Orbis
"""
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            msg = pattern.format(team=team, )
            msg_object = NotificationToTeamMessage(team=team, custom_message=msg)
            dispatcher.dispatch_raw_message(msg=msg_object)
        except Exception as e:
            print(e)


# python manage.py runscript debug
def run():
    main()
