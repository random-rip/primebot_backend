import logging
import threading
import time

from app_prime_league.models import Match, Team
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


def update_teams_and_matches():
    """Updates teams and matches."""
    start_time = time.time()
    teams = Team.objects.get_teams_to_update()
    logger.info(f"Updating {len(teams)} teams...")
    update_teams(teams=teams)
    logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    uncompleted_matches = Match.current_split_objects.get_matches_to_update()
    logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
    update_uncompleted_matches(matches=uncompleted_matches)
    logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
    updated_teams = [x.id for x in teams]
    updated_matches = [x.match_id for x in uncompleted_matches]
    return {
        "TEAMS": updated_teams,
        "MATCHES": updated_matches,
    }
