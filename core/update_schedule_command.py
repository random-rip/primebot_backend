import logging
import pydoc
from abc import ABC, abstractmethod
from typing import Type

from django.core.management import get_commands
from django_q.models import Schedule, Task

from core.commands import ScheduleCommand

logger = logging.getLogger("updates")


def activate_correct_update_schedule(task: Task):
    if not task.success:
        logger.warning(f"Task {task} was not successful. Aborting...")
        return

    current_command_path: str = task.func.rpartition('.')[0]
    CurrentCommand: Type[UpdateScheduleCommand] = pydoc.locate(current_command_path)
    if not CurrentCommand.is_time_exceeded():
        logger.info(f"Time of Schedule {CurrentCommand.name} not exceeded yet.")
        return

    next_command = CurrentCommand.next_command
    try:
        NextCommand: Type[UpdateScheduleCommand] = pydoc.locate(
            f"app_prime_league.management.commands.{next_command}.Command"
        )
        new_schedule = NextCommand()._schedule()
    except Exception as e:
        logger.error(f"Failed to create schedule '{next_command}': {e}")
        return

    try:
        Schedule.objects.get(name=CurrentCommand.name).delete()
    except Schedule.DoesNotExist:
        logger.warning(
            f"Schedule '{CurrentCommand.name}' does not exist. Reverting creation of schedule '{next_command}'."
        )
        new_schedule.delete()
    except Exception as e:
        logger.error(
            f"Failed to delete schedule '{CurrentCommand.name}': {e}. Reverting creation of schedule '{next_command}'."
        )
        new_schedule.delete()
    else:
        logger.info(f"Created schedule '{next_command}' and deleted schedule '{CurrentCommand.name}'.")


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

    def _schedule(self) -> Schedule:
        s = Schedule(
            name=self.name,
            func=self.func_path,
            schedule_type=Schedule.CRON,
            cron=self.cron(),
            hook="core.update_schedule_command.activate_correct_update_schedule",
        )
        s.next_run = s.calculate_next_run()
        s.save()
        return s
