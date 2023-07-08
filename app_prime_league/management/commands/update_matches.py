import logging
import threading
import time

from django_q.models import Schedule

from app_prime_league.models import Match
from core.commands import ScheduleCommand
from core.updater.matches_check_executor import update_uncompleted_matches

thread_local = threading.local()
logger = logging.getLogger("updates")


class Command(ScheduleCommand):

    @staticmethod
    def func():
        start_time = time.time()
        uncompleted_matches = Match.objects.get_matches_to_update()
        logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
        update_uncompleted_matches(matches=uncompleted_matches)
        logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")

    def _schedule(self):
        s = Schedule(
            name="Update Matches",
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='5/15 * * * *',
        )
        s.next_run = s.calculate_next_run()
        s.save()
