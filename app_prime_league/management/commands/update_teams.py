import logging
import threading
import time

from django_q.models import Schedule

from app_prime_league.models import Team
from core.commands import ScheduleCommand
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


class Command(ScheduleCommand):
    @staticmethod
    def func():
        start_time = time.time()
        teams = Team.objects.all()
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(teams=teams, )
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")

    def _schedule(self):
        s = Schedule(
            name="Update Teams",
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='0/30 * * * *',
        )
        s.next_run = s.calculate_next_run()
        s.save()
