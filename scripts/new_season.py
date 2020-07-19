from app_prime_league.models import Team
from app_prime_league.teams import add_or_update_players, add_games
from data_crawling.api import crawler
from parsing.parser import TeamHTMLParser, TeamWrapper


def main():
    teams = Team.objects.get_watched_teams()
    for i in teams:
        parser = TeamWrapper(team_id=i.id).parser

        add_or_update_players(parser.get_members(), i)
        add_games(parser.get_matches(), i)


def run():
    main()
