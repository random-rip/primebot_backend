from datetime import datetime

import pytz

from app_prime_league.models import Game
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    start_date = datetime(2020, 6, 8).astimezone(pytz.timezone("Europe/Berlin"))
    current_date = datetime.now().astimezone(pytz.timezone("Europe/Berlin"))
    game_day = ((current_date - start_date) / 7).days + 1
    games = Game.objects.filter(game_day=game_day, game_closed=False)
    for i in games:
        settings = dict(i.team.setting_set.all().values_list("attr_name", "attr_value"))
        if settings.get("weekly_op_link", True):
            TelegramMessagesWrapper.send_new_game_day(i)


def run():
    main()
