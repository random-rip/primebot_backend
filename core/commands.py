import inspect
import pydoc
from abc import ABC, abstractmethod

from django.core.management import BaseCommand


class ScheduleCommand(BaseCommand, ABC):
    """
    Command to create schedules for the q-cluster or to execute jobs directly.
    """

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
        self.func_path = self._validated_func()

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule', action='store_true', help='Schedule the job to the Q cluster'
        )
        self._add_arguments(parser)

    def _add_arguments(self, parser):
        """add arguments for parser"""
        pass

    def _func_path(self) -> str:
        """Returns string dotted path to the related function. Can be overwritten for different function."""
        return f"{inspect.getmodule(self.func).__name__}.{type(self).__name__}.func"

    def _validated_func(self) -> str:
        """Validates if the string dotted function path points to an executable function."""
        if not isinstance(self._func_path(), str):
            raise TypeError('Type str expected! The function has to be given by a dotted path')

        if not callable(pydoc.locate(self._func_path())):
            raise TypeError('_func_path() returns path to a not callable function')

        return self._func_path()

    @staticmethod
    @abstractmethod
    def func():
        pass

    @abstractmethod
    def _schedule(self):
        pass

    def handle(self, *args, **options):
        if options['schedule']:
            self._schedule()
            self.stdout.write("Created a schedule")
            return
        self.func()
