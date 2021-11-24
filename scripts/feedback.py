from app_prime_league.models import Team
from communication_interfaces.message_dispatcher import MessageDispatcher


def main():
    teams = Team.objects.get_watched_teams()
    pattern = """
Hallo {team.name}, 

die Gruppenphasen- und Tiebreakerspiele sind zuende, und damit geht der PrimeBot in die Winterpause.
Die kommenden Tage sind noch Playoffs, wo wir den Teams viel Erfolg wünschen. 🏆
Außerdem freuen uns über euer Feedback!
Da wir bemüht sind den Primebot weiterhin zu verbessern, möchten wir in einem kurzen Feedback fragen,
welche Features euch wirklich interessieren und welche Features euch noch fehlen.
Link zum 🔥[Feedback](https://feedback.primebot.me/)🔥.

Sternige Grüße
Grayknife und Orbis
"""
    for team in teams:
        try:
            print(team)
            dispatcher = MessageDispatcher(team)
            msg = pattern.format(team=team, )
            dispatcher.dispatch_raw_message(msg=msg)
        except Exception as e:
            print(e)


# python manage.py runscript debug
def run():
    main()
