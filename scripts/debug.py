from app_prime_league.models import Team, Game
from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import WeeklyNotificationMessage, NewLineupNotificationMessage
from parsing.parser import LogSchedulingAutoConfirmation


def main():
    team = Team.objects.get(id=125071)
    game = Game.objects.get(game_id=696320)
    message = WeeklyNotificationMessage(team, game)
    log = LogSchedulingAutoConfirmation("1614976397", "Janek", "None")
    # message = ScheduleConfirmationNotification(team, game, log)
    lineup_message = NewLineupNotificationMessage(team, game)
    MessageDispatcher(team=team).dispatch(NewLineupNotificationMessage, game=game, )


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
