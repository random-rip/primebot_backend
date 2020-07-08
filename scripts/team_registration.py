import time

from app_prime_league.teams import register_team


# python manage.py runscript team_registration --script-args <TEAM_ID> <TG_GROUP_ID>
def run(*args):
    start_time = time.time()
    if len(args) != 2:
        print("TEAM_ID first, TG_GROUP_ID second! Not more or less than that.")
        return
    team_id = args[0]
    tg_group_id = args[1]
    register_team(team_id, tg_group_id)
    duration = time.time() - start_time
    print(f"Finished all in {duration} seconds")
