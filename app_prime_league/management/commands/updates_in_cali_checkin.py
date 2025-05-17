import logging
from datetime import datetime

from django.utils import timezone
from django.utils.timezone import make_aware

from app_prime_league.models import Split
from core.update_schedule_command import UpdateScheduleCommand

logger = logging.getLogger("updates")


class Command(UpdateScheduleCommand):
    help = """Update teams and matches that are in the calibration phase."""
    next_command = "updates_in_cali_live"
    name = "Update Teams and Matches in Calibration Stage"

    @staticmethod
    def func(notify=True):
        from core.updater.call_executors import update_teams_and_matches

        return update_teams_and_matches(notify=notify)

    @staticmethod
    def is_time_exceeded() -> bool:  # FIXME
        """
        Returns True if the calibration stage checkin
        :return: True if its passed 2 PM
        """
        logger.info('Checkin time exceeded')
        start = Split.objects.get_current_split().calibration_stage_start
        with_time = datetime(
            year=start.year,
            month=start.month,
            day=start.day,
            hour=13,
            minute=45,
        )
        with_time = make_aware(with_time)
        now = timezone.now()
        is_exceeded = with_time <= now
        logger.info(
            f"Calibration stage start: {with_time} --- " f"Current time: {now} --- " f"Time exceeded: {is_exceeded}"
        )
        return is_exceeded

    def cron(self) -> str:
        return "*/10 * * * *"
