from app_prime_league.models import Game
from telegram_interface.tg_singleton import TelegramMessagesWrapper
from utils.utils import current_game_day


def main():
    game_day = current_game_day()
    games = Game.objects.filter(game_day=game_day, game_closed=False)
    for i in games:
        settings = dict(i.team.setting_set.all().values_list("attr_name", "attr_value"))
        if settings.get("weekly_op_link", True):
            TelegramMessagesWrapper.send_new_game_day(i)


def run():
    main()
