import time
from datetime import datetime

from app_prime_league.models import Team
from app_prime_league.teams import add_or_update_players, add_games, update_team
from parsing.parser import TeamWrapper


def main():
    start_time = time.time()
    print(f"Starting Updates at {datetime.now()}")
    teams = Team.objects.all()

    for i in teams:
        parser = TeamWrapper(team_id=i.id).parser
        update_team(parser, team_id=i.id)
        add_or_update_players(parser.get_members(), i)
        if i.telegram_channel_id is not None:
            game_ids = parser.get_matches()
            if len(game_ids) != len(i.games_against.all()):
                print(i)
                add_games(game_ids, i)

    print(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")


# python manage.py runscript team_updates
def run():
    main()
