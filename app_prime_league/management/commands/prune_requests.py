from django.core.management import call_command
from django_q.models import Schedule

from core.commands import ScheduleCommand


class Command(ScheduleCommand):
    """
    Command to prune old requests from the database. By default, it prunes requests that are older than 6 months.
    """

    def _schedule(self):
        s = Schedule(
            name="Prune requests",
            func=self.func_path,
            args="6, 'months'",
            schedule_type=Schedule.DAILY,
        )
        s.next_run = s.calculate_next_run()
        s.save()

    @staticmethod
    def func(amount: int = 6, unit: str = "months") -> None:
        call_command(
            "purgerequests",
            amount,
            unit,
            noinput=False,  # Weird behavior, but setting it to True asks for confirmation in call_command
        )
