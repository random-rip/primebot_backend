from app_prime_league.models import Team
from parsing.parser import MatchWrapper


def main():
    team = Team.objects.get_team(111464)
    wrapper = MatchWrapper(650878, team)
    parser = wrapper.parser
    print(parser.get_comments())


def run():
    main()
