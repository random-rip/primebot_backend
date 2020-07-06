from app_prime_league.models import Team
from app_prime_league.teams import add_players, add_games
from data_crawling.api import crawler
from parsing.regex_operations import TeamHTMLParser, TeamWrapper


def main():
    teams = Team.objects.get_watched_teams()
    for i in teams:
        parser = TeamWrapper(team_id=i.id).parser

        add_players(parser, i)
        add_games(parser, i)


def run():
    main()
