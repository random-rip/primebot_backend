import logging
import time
from datetime import datetime

from app_prime_league.models import Team
from app_prime_league.teams import add_or_update_players, add_games, update_team
from parsing.parser import TeamWrapper, WebsiteIsNoneException


def main():
    start_time = time.time()
    logger = logging.getLogger("periodic_logger")
    logger.info(f"Starting Team Updates at {datetime.now()}")
    teams = Team.objects.all()

    for team in teams:
        logger.info(f"Checking {team}... ")
        try:
            parser = TeamWrapper(team_id=team.id).parser
        except WebsiteIsNoneException as e:
            logger.info(f"{e}, Skipping!")
            continue
        update_team(parser, team_id=team.id)
        add_or_update_players(parser.get_members(), team)
        if team.telegram_id is not None:
            game_ids = parser.get_matches()
            if len(game_ids) != len(team.games_against.all()):
                logger.debug(f"Checking {len(game_ids)} games for {team}... ")
                add_games(game_ids, team)

    logger.info(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")


def run():
    main()
