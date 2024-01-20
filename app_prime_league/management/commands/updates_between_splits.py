import logging
import threading
import time

from django.core.management import call_command
from django.utils import timezone
from django_q.models import Schedule

from app_prime_league.models import Split, Team
from core.commands import ScheduleCommand
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")

name = "Updates between splits"


def activate_updates_in_calibration_stage(task):
    """
    Checks if the calibration stage started and if so, deletes this schedule and
    creates the calibration stage schedule.
    """

    if not task.success:
        logger.warning(f"Task {task} was not successful. Aborting...")
        return

    calibration_start = Split.objects.get_current_split().calibration_stage_start
    if calibration_start < timezone.now().date():
        return

    next_command = "updates_in_calibration_stage"
    logger.info(f"Creating schedule '{next_command}' and deleting schedule '{name}'...")
    call_command(next_command, "--schedule")
    Schedule.objects.get(name=name).delete()
    logger.info(f"Created schedule '{next_command}' and deleted schedule '{name}'.")


class Command(ScheduleCommand):
    help = """Update teams that are registered (usually between splits)."""

    @staticmethod
    def func():
        start_time = time.time()
        teams = Team.objects.get_registered_teams()
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(
            teams=teams,
        )
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    def _schedule(self):
        s = Schedule(
            name=name,
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='0/30 * * * *',
            hook='app_prime_league.management.commands.update_registered_teams.activate_updates_in_calibration_stage',
        )
        s.next_run = s.calculate_next_run()
        s.save()
