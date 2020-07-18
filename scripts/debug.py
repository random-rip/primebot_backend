from datetime import datetime

import requests
import re

from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from comparing.member_comparer import MemberComparer
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper, send_message


def main():
    crawler = Crawler(local=False)
    website = crawler.get_team_website(105878)
    parser = TeamHTMLParser(website)
    team = Team(id=105878)
    members = parser.get_members()
    print(members[0][0])
    comparer = MemberComparer(105878, members)
    comparer.compare_members()

def run():
    main()
