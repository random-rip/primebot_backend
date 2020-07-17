from datetime import datetime

import requests
import re

from bs4 import BeautifulSoup
from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from app_prime_league.teams import add_players, add_games, update_team
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser, TeamWrapper
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    teams = Team.objects.all()

    for i in teams:
        parser = TeamWrapper(team_id=i.id).parser
        update_team(parser, i)
        add_players(parser.get_members(), i)


# Command to run this file:
# python manage.py runscript team_updates
def run():
    main()
