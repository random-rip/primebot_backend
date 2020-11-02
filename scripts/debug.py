from app_prime_league.models import Team
from utils.utils import current_game_day


def main():
    game_day = current_game_day()

    teams = Team.objects.get_watched_team_of_current_split()
    print(teams)
    for team in teams:
        print(team)
        if team.value_of_setting("weekly_op_link"):
            next_match = team.games_against.filter(game_day=game_day).first()
            print(next_match)


def run():
    main()
