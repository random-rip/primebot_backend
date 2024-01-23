from django.utils import timezone

from app_prime_league.models import Split
from core.update_schedule_command import UpdateScheduleCommand


class Command(UpdateScheduleCommand):
    help = """Update teams that are registered and matches ."""
    next_command = "updates_in_group_stage_and_playoffs"
    name = "Update Teams and Matches between Calibration and Group Stage"

    def _func_path(self) -> str:
        return "core.updater.call_executors.update_teams_and_matches"

    @staticmethod
    def is_time_exceeded() -> bool:
        """
        Returns True if the group stage starts
        """
        group_stage_start = Split.objects.get_current_split().group_stage_start
        return group_stage_start <= timezone.now().date()

    def cron(self) -> str:
        return "5/15 * * * *"
