import logging

from app_prime_league.models import Team
from communication_interfaces.telegram_interface.tg_singleton import TelegramMessagesWrapper
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    logger = logging.getLogger("notifications_logger")
    logger.info(f"Start Sending Weekly Notifications...")
    teams = Team.objects.filter(id__in=[89678, 102301])
    print(teams)
    for team in teams:
        print(teams)
        if team.value_of_setting("weekly_op_link"):
            logger.debug(f"Sending Weekly Notification to {team}...")
            next_match = team.games_against.filter(game_day=game_day).first()
            if next_match is not None:
                TelegramMessagesWrapper.send_new_game_day(next_match, team.value_of_setting("pin_weekly_op_link"))


def run():
    main()
