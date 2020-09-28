from app_prime_league.models import Game, Team
from telegram_interface.tg_singleton import TelegramMessagesWrapper
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    teams = Team.objects.filter(telegram_id__isnull=False)

    for team in teams:
        print(team)
        settings = dict(team.setting_set.all().values_list("attr_name", "attr_value"))
        if settings.get("weekly_op_link", True):
            next_match = team.games_against.filter(game_day=game_day).first()
            print(next_match)
            TelegramMessagesWrapper.send_new_game_day(next_match, settings.get("pin_weekly_op_link", True))


def run():
    main()
