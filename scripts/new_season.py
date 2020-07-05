from app_prime_league.models import Team, Game, Player
from app_prime_league.teams import add_players, add_games
from comparing.game_comparer import GameMetaData
from data_crawling.api import Crawler, crawler
from parsing.regex_operations import TeamHTMLParser
from telegram_interface import send_message


def main():
    teams = Team.objects.get_watched_teams()
    for i in teams:
        parser = TeamHTMLParser(crawler.get_team_website(i.id))

        add_players(parser, i)
        add_games(parser, i)


def run():
    main()
