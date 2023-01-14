import logging
import threading
import time

from django_q.models import Schedule

from app_prime_league.models import Team, Match
from core.commands import ScheduleCommand
from core.updater.matches_check_executor import update_uncompleted_matches
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
        uncompleted_matches = Match.objects.get_matches_to_update()
        logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
        update_uncompleted_matches(matches=uncompleted_matches)
        logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")

    def _schedule(self):
        s = Schedule(
            name="Update Teams and Matches",
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron='*/2 * * * *',
        )
        s.next_run = s.calculate_next_run()
        s.save()
