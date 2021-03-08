from app_prime_league.models import Team, Game
from communication_interfaces.messages import WeeklyNotificationMessage, NewLineupNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, EnemyNewTimeSuggestionsNotificationMessage, \
    ScheduleConfirmationNotification
from discord_interface.discord_bot import DiscordBot
from parsing.parser import LogSchedulingAutoConfirmation


def main():
    # team = Team.objects.get(id=123906)
    # game = Game.objects.get(game_id=650854)
    # weekly_message = WeeklyNotificationMessage(team, game)
    # log = LogSchedulingAutoConfirmation("1614976397", "Janek", "None")
    # message = ScheduleConfirmationNotification(team, game, log)
    # lineup_message = NewLineupNotificationMessage(team, game)
    # print(message.message)
    # print(lineup_message.message)
    bot = DiscordBot.send()

# Command to run this file:
# python manage.py runscript debug
def run():
    main()
