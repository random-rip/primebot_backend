import logging

from app_prime_league.models import Team
from telegram_interface.tg_singleton import TelegramMessagesWrapper
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    logger = logging.getLogger("notifications_logger")
    logger.info(f"Start Sending Weekly Notifications...")
    teams = Team.objects.get_watched_team_of_current_split()
    for team in teams:
        settings = dict(team.setting_set.all().values_list("attr_name", "attr_value"))
        if settings.get("weekly_op_link", True):
            logger.debug(f"Sending Weekly Notification to {team}...")
            next_match = team.games_against.filter(game_day=game_day).first()
            TelegramMessagesWrapper.send_new_game_day(next_match, settings.get("pin_weekly_op_link", True))


def run():
    main()
