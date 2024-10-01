import logging
import threading
import time
from datetime import timedelta
from typing import Tuple

from django.utils import timezone

from app_prime_league.models import Match, Team
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


def get_priority_teams_and_matches() -> Tuple[set[Team], set[Match]]:
    """
    Iterates over matches within the next 3 Weeks (+ last 2 days) and sort by -updated_at.
    Then takes the first 1-900 matches and its corresponding teams until the summation of Teams and Matches
    reaches 900.
    :return:
    """
    now = timezone.now()
    three_weeks_later = now + timedelta(weeks=3)
    all_matches = Match.current_split_objects.get_matches_to_update().order_by('-updated_at')
    high_priority_matches = all_matches.filter(begin__lte=three_weeks_later)
    low_priority_matches = all_matches.filter(begin__gt=three_weeks_later)

    matches_to_update = set()
    teams_to_update = set()
    update_count = 0

    def add_matches_and_teams(matches: list[Match]):
        nonlocal update_count
        for match in matches:
            if update_count >= 900:
                break
            if match not in matches_to_update:
                matches_to_update.add(match)
                update_count += 1
            if match.team not in teams_to_update:
                teams_to_update.add(match.team)
                update_count += 1
            if match.enemy_team not in teams_to_update:
                teams_to_update.add(match.enemy_team)
                update_count += 1

    add_matches_and_teams(high_priority_matches)
    if update_count < 900:
        add_matches_and_teams(low_priority_matches)
    return teams_to_update, matches_to_update


def update_teams_and_matches():
    """Updates teams and matches."""
    start_time = time.time()
    teams, uncompleted_matches = get_priority_teams_and_matches()
    logger.info(f"Updating {len(teams)} teams...")
    update_teams(teams=teams)
    logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
    update_uncompleted_matches(matches=uncompleted_matches)
    logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
