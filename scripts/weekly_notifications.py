import logging

from app_prime_league.models import Team
from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import WeeklyNotificationMessage
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    logger = logging.getLogger("notifications")
    logger.info(f"Start Sending Weekly Notifications...")
    teams = Team.objects.get_watched_team_of_current_split()
    for team in teams:
        try:
            next_match = team.games_against.filter(game_day=game_day).last()
            if next_match is not None:
                logger.debug(f"Sending Weekly Notification to {team}...")
                MessageDispatcher(team=team).dispatch(WeeklyNotificationMessage, game=next_match)
        except Exception as e:
            logger.error(f"Error {team}: {e}")


def run():
    main()
