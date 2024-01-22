from django.utils import timezone

from app_prime_league.models import Split
from core.update_schedule_command import UpdateScheduleCommand


class Command(UpdateScheduleCommand):
    help = """Update teams and matches that are in the calibration phase."""
    next_command = "updates_between_calibration_and_group_stage"
    name = "Update Teams and Matches in Calibration Stage"

    def _func_path(self) -> str:
        return "core.updater.update.update"

    @staticmethod
    def is_time_exceeded() -> bool:
        """
        Returns True if the calibration stage ended (two days after calibration stage start)
        :return:
        """
        calibration_end_with_puffer = Split.objects.get_current_split().calibration_stage_start + timezone.timedelta(
            days=2
        )
        return calibration_end_with_puffer <= timezone.now().date()

    def cron(self) -> str:
        return "*/2 * * * *"
