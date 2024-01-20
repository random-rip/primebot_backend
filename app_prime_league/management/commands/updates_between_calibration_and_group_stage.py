import logging
import threading
import time

from django.core.management import call_command
from django.utils import timezone
from django_q.models import Schedule

from app_prime_league.models import Match, Split, Team
from core.commands import ScheduleCommand
from core.updater.matches_check_executor import update_uncompleted_matches
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")

name = "Update Teams and Matches between Calibration and Group Stage"


def activate_updates_in_group_stage_and_playoffs(task):
    """
    Checks if the group stage starts and if so, deletes the schedule and
    creates the group stage and playoffs schedule.
    """
    if not task.success:
        logger.warning(f"Task {task} was not successful. Aborting...")
        return

    group_stage_start = Split.objects.get_current_split().group_stage_start
    if group_stage_start > timezone.now().date():
        return

    next_command = "updates_in_group_stage_and_playoffs"
    logger.info(f"Creating schedule '{next_command}' and deleting schedule '{name}'...")
    call_command(next_command, "--schedule")
    Schedule.objects.get(name=name).delete()
    logger.info(f"Created schedule '{next_command}' and deleted schedule '{name}'.")


class Command(ScheduleCommand):
    help = """Update teams that are registered and matches ."""

    @staticmethod
    def func():
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

    def _schedule(self):
        s = Schedule(
            name=name,
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='5/15 * * * *',
            hook='app_prime_league.management.commands.updates_in_group_stage_and_playoffs.activate_updates_in_group_stage_and_playoffs',
        )
        s.next_run = s.calculate_next_run()
        s.save()
