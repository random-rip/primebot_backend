import logging
import time
from datetime import timedelta
from typing import Tuple

from django.utils import timezone

from app_prime_league.models import Match, Split, Team
from core.update_schedule_command import UpdateScheduleCommand
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

logger = logging.getLogger("updates")

MAX_TEAMS = 100
MAX_UPDATES = 400


def get_priority_teams_and_matches() -> Tuple[set[Team], set[Match]]:
    """
    Retrieve relevant teams and matches to update.
    If it is between 0 and 2 AM on a Monday, Thursday or Sunday, all teams are updated (max 700).
    If it is between 3 and 5 AM, all matches are updated (max 700).
    Otherwise, it iterates over matches within the next 3 Weeks (+ last 2 days) and sort by updated_at. Then
    it iterates over the matches and adds the team and enemy team to the set of teams to update (max 100 teams) and
    in summation the matches to update (max 400). If 400 is not reached, it takes also matches with a begin date
    after the 3 weeks. Teams and matches are only added once.
    """
    now = timezone.now()

    if now.weekday() in [0, 3, 6] and 0 <= now.hour < 2:  # Monday, Thursday, Sunday
        logger.info("It is monday between 0 and 2: Updating all teams...")
        # If the time is between 0 and 2 AM on a Monday, Thursday or Sunday, we update all teams for potential
        # new matches and general team updates like the name
        teams_to_update = Team.objects.get_teams_to_update().order_by('updated_at')[:MAX_UPDATES]
        return set(teams_to_update), set()

    if 2 <= now.hour < 5:
        # If the time is between 3 and 5 AM on a Monday, we update all matches
        logger.info("It is between 3 and 5 AM: Updating all matches...")
        matches_to_update = Match.current_split_objects.get_matches_to_update().order_by('updated_at')[:MAX_UPDATES]
        return set(), set(matches_to_update)

    logger.info("It is not between 3 and 5 AM: Updating priority matches and teams...")
    update_count = 0
    matches_to_update = set()
    teams_to_update = set()

    def add_matches_and_teams(matches: list[Match]):
        nonlocal update_count
        for match in matches:
            if update_count >= MAX_UPDATES:
                break
            if match not in matches_to_update and update_count < MAX_UPDATES:
                matches_to_update.add(match)
                update_count += 1
            if match.team not in teams_to_update and len(teams_to_update) < MAX_TEAMS and update_count < MAX_UPDATES:
                teams_to_update.add(match.team)
                update_count += 1
            if (
                match.enemy_team not in teams_to_update
                and len(teams_to_update) < MAX_TEAMS
                and update_count < MAX_UPDATES
            ):
                teams_to_update.add(match.enemy_team)
                update_count += 1

    three_weeks_later = now + timedelta(weeks=3)
    all_matches = Match.current_split_objects.get_matches_to_update().order_by('updated_at')  # oldest updated first
    high_priority_matches = all_matches.filter(begin__lte=three_weeks_later)
    low_priority_matches = all_matches.filter(begin__gt=three_weeks_later)
    add_matches_and_teams(high_priority_matches)
    add_matches_and_teams(low_priority_matches)

    return teams_to_update, matches_to_update


class Command(UpdateScheduleCommand):
    help = """Update teams and matches that are in the group stage and playoffs."""
    next_command = "updates_between_splits"
    name = "Update Teams and Matches in Group Stage and Playoffs"

    @staticmethod
    def func():
        start_time = time.time()
        teams, uncompleted_matches = get_priority_teams_and_matches()
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(teams=teams)
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

        start_time = time.time()
        logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
        update_uncompleted_matches(matches=uncompleted_matches)
        logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
        return {
            "TEAMS": teams,
            "MATCHES": uncompleted_matches,
        }

    @staticmethod
    def is_time_exceeded() -> bool:
        """
        Returns True if the playoffs ended (two days after playoffs end because of completed matches).
        If there are still open matches, it returns False.
        """
        if Match.current_split_objects.filter(closed=False).exists():
            return False
        playoffs_end = Split.objects.get_current_split().playoffs_end + timezone.timedelta(days=2)
        return playoffs_end < timezone.now().date()

    def cron(self) -> str:
        return "5/15 * * * *"
