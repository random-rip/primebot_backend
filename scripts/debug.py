from datetime import datetime

import requests
import re

from telegram import Bot
from telegram.ext import Updater, CommandHandler

from app_prime_league.models import Team, Game
from app_prime_league.teams import register_team
from data_crawling.api import crawler, Crawler
from parsing.parser import MatchWrapper, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime, \
    TeamHTMLParser
from prime_league_bot import settings
from telegram_interface.botfather import BotFather
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def main():
    crawler = Crawler(local=False)
    parser = TeamHTMLParser(crawler.get_team_website(112004))
    print(parser.get_team_name())
    print(parser.get_team_tag())
    team = Team.objects.get(id=112004)
    print(team.games_against.values_list("enemy_team_id", flat=True))
    # for index,team in enumerate([89678,
    #           91700,
    #           93008,
    #           93935,
    #           95568,
    #           97008,
    #           105731,
    #           105875,
    #           105878,
    #           105959,
    #           107117,
    #           108272,
    #           108434,
    #           108626,
    #           110006,
    #           110231,
    #           110240,
    #           110387,
    #           110489,
    #           110582,
    #           110801,
    #           111092,
    #           111779,
    #           111914,
    #           112004,
    #           112070,
    #           112154,
    #           112262,
    #           112439,
    #           112460,
    #           112532,
    #           112544,
    #           112550,
    #           112670,
    #           112910,
    #           114463,
    #           114490,
    #           116107,
    #           116380,
    #           117790,
    #           118459,
    #           118615,
    #           118882,
    #           119422,
    #           119482,
    #           120211,
    #           120301,
    #           120391,
    #           120460,
    #           120499,
    #           120757,
    #           121243,
    #           121423,
    #           121447,
    #           121723, ]):
    #     register_team(team, index)

# Command to run this file:
# python manage.py runscript debug
def run():
    main()
