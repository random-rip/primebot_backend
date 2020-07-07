from app_prime_league.models import Game
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    game_day = 6
    games = Game.objects.filter(game_day=game_day, game_closed=False)
    for i in games:
        if i.team.setting_set.get("weekly_op_link", True):
            TelegramMessagesWrapper.send_new_game_day(i)


def run():
    main()
