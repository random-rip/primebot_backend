import logging
import threading
import time

from django.utils import timezone

from app_prime_league.models import Split, Team
from core.update_schedule_command import UpdateScheduleCommand
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


class Command(UpdateScheduleCommand):
    help = """Update teams that are registered and matches ."""
    next_command = "updates_in_group_stage_and_playoffs"
    name = "Update Teams and Matches between Calibration and Group Stage"

    @staticmethod
    def func(notify=True):
        start_time = time.time()
        teams = Team.objects.get_teams_to_update()
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(teams=teams, notify=notify)
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    @staticmethod
    def is_time_exceeded() -> bool:
        """
        Returns True if the group stage starts
        """
        group_stage_start = Split.objects.get_current_split().group_stage_start
        is_exceeded = group_stage_start <= timezone.now().date()
        logger.info(f"Checking if group stage started: {is_exceeded}")
        return is_exceeded

    def cron(self) -> str:
        return "5/15 * * * *"
