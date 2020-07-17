from datetime import datetime

import requests
import re

from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    crawler = Crawler(local=False)
    parser = TeamHTMLParser(crawler.get_team_website(121723))
    print(parser.get_current_division())

# print(parser.get_team_name())
# print(parser.get_team_tag())
# print(int("112004-1-esport-club-frankfurt-goethe-5-2-0"))


# Command to run this file:
# python manage.py runscript debug
def run():
    main()
