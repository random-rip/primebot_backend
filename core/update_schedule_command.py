import logging
import pydoc
from abc import ABC, abstractmethod
from typing import Type

from django.core.management import call_command, get_commands
from django_q.models import Schedule, Task

from core.commands import ScheduleCommand

logger = logging.getLogger("updates")


def activate_correct_update_schedule(task: Task):
    if not task.success:
        logger.warning(f"Task {task} was not successful. Aborting...")
        return

    klass_path: str = task.func.rpartition('.')[0]
    klass: Type[UpdateScheduleCommand] = pydoc.locate(klass_path)
    if not klass.is_time_exceeded():
        logger.info(f"Time of Schedule {klass.name} not exceeded yet.")
        return
    next_command = klass.next_command
    name = klass.name
    logger.info(f"Creating schedule '{next_command}' and deleting schedule '{name}'...")
    call_command(next_command, "--schedule")
    Schedule.objects.get(name=name).delete()
    logger.info(f"Created schedule '{next_command}' and deleted schedule '{name}'.")


class UpdateScheduleCommand(ScheduleCommand, ABC):
    """
    Update Schedules depends on each other. You can create hooks between them.
    """

    next_command: str = None
    name: str = None

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
        if self.next_command is None:
            raise ValueError("next_command is not set!")
        if self.next_command not in get_commands():
            raise ValueError(f"next_command '{self.next_command}' is not a valid command!")
        if self.name is None:
            raise ValueError("name is not set!")

    @staticmethod
    @abstractmethod
    def is_time_exceeded() -> bool:
        """
        Checks if the time is exceeded to execute this command.
        :return:
        """

    @abstractmethod
    def cron(self) -> str:
        """
        Returns the cron string for this command.
        :return:
        """

    def _schedule(self):
        s = Schedule(
            name=self.name,
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron=self.cron(),
            hook="core.update_schedule_command.activate_correct_update_schedule",
        )
        s.next_run = s.calculate_next_run()
        s.save()
