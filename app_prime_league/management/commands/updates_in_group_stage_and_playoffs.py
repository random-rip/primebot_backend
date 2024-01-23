from django.utils import timezone

from app_prime_league.models import Split
from core.update_schedule_command import UpdateScheduleCommand


class Command(UpdateScheduleCommand):
    help = """Update teams and matches that are in the group stage and playoffs."""
    next_command = "updates_between_splits"
    name = "Update Teams and Matches in Group Stage and Playoffs"

    @staticmethod
    def func():
        from core.updater.call_executors import update_teams_and_matches

        update_teams_and_matches()

    @staticmethod
    def is_time_exceeded() -> bool:
        """Returns True if the playoffs ended (two days after playoffs end because of completed matches)."""
        playoffs_end = Split.objects.get_current_split().playoffs_end + timezone.timedelta(days=2)
        return playoffs_end < timezone.now().date()

    def cron(self) -> str:
        return "5/15 * * * *"
