from app_prime_league.models import Team
from app_prime_league.teams import add_players, add_games
from data_crawling.api import crawler
from parsing.regex_operations import TeamHTMLParser


def main():
    teams = Team.objects.get_watched_teams()
    for i in teams:
        parser = TeamHTMLParser(crawler.get_team_website(i.id))

        add_players(parser, i)
        add_games(parser, i)


def run():
    main()
