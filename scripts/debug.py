from app_prime_league.models import Team
from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import WeeklyNotificationMessage, ScheduleConfirmationNotification, \
    NewLineupNotificationMessage, OwnNewTimeSuggestionsNotificationMessage
from parsing.parser import LogSchedulingAutoConfirmation


def main():
    team = Team.objects.get(id=132664)
    game = team.games_against.first()
    message = WeeklyNotificationMessage(team, game)
    log = LogSchedulingAutoConfirmation("1614976397", "Janek", "None")
    # message = ScheduleConfirmationNotification(team, game, log)
    # lineup_message = NewLineupNotificationMessage(team, game)
    print(message.message)
    print(message.notification_wanted())
    print(message.can_be_pinned())
    MessageDispatcher(team=team).dispatch(OwnNewTimeSuggestionsNotificationMessage, game=game)


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
