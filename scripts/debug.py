from datetime import datetime

import requests
import re

from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from data_crawling.api import crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    game = Game.objects.get(game_id=596833)
    TelegramMessagesWrapper.send_new_game_day(game)
    TelegramMessagesWrapper.send_new_lineup_of_enemies(game)
    TelegramMessagesWrapper.send_new_suggestion(game)
    TelegramMessagesWrapper.send_new_suggestion_of_enemies(game)
    TelegramMessagesWrapper.send_scheduling_confirmation(game, LogChangeTime("123546412","",""))


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
