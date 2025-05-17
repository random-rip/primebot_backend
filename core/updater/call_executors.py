import logging
import threading
import time

from app_prime_league.models import Match, Team
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


def update_teams_and_matches(notify: bool):
    """Updates teams and matches."""
    start_time = time.time()
    teams = Team.objects.get_teams_to_update()
    logger.info(f"Updating {len(teams)} teams...")
    update_teams(teams=teams, notify=notify)
    logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    uncompleted_matches = Match.current_split_objects.get_matches_to_update()
    logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
    update_uncompleted_matches(matches=uncompleted_matches, notify=notify)
    logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
    return {
        "TEAMS": [str(x) for x in teams],
        "MATCHES": [str(x) for x in uncompleted_matches],
    }
