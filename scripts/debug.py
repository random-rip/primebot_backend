import requests
import re

from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team
from data_crawling.api import crawler
from parsing.regex_operations import MatchWrapper
from prime_league_bot import settings
from telegram_interface.botfather import BotFather


def main():
    team = Team.objects.get(id=105959)
    parser = MatchWrapper("597523", team).parser
    parser.get_enemy_lineup()


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
