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
    help = """Update teams that are registered (usually between splits)."""
    next_command = "updates_in_calibration_stage"
    name = "Updates between splits"

    @staticmethod
    def func(notify=True):
        start_time = time.time()
        teams = Team.objects.get_registered_teams().order_by("updated_at")  # oldest updated first
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(
            teams=teams,
            notify=notify,
        )
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    @staticmethod
    def is_time_exceeded() -> bool:
        """Returns True if the calibration stage starts"""
        current_split = Split.objects.get_current_split()
        calibration_start = current_split.calibration_stage_start
        current_date = timezone.now().date()
        if current_split.playoffs_end < current_date:  # current split already ended
            return False
        return calibration_start <= current_date

    def cron(self):
        return "0/30 * * * *"
