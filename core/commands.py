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
        self.func_path = self._validate_func_path(self._func_path())

    def add_arguments(self, parser):
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Schedule the job to the Q cluster',
        )
        self._add_arguments(parser)

    def _add_arguments(self, parser):
        """add arguments for parser"""
        pass

    def _func_path(self) -> str:
        """Returns string dotted path to the related function. Can be overwritten for different function."""
        return f"{inspect.getmodule(self.func).__name__}.{type(self).__name__}.func"

    def _validate_func_path(self, func_path) -> str:
        """Validates if the given string dotted function path points to an executable function."""
        if not isinstance(func_path, str):
            raise TypeError('Type str expected! The function has to be given by a dotted path')

        if not callable(pydoc.locate(func_path)):
            raise TypeError('func_path returns path to a not callable function')

        return func_path

    @staticmethod
    def func():
        raise NotImplementedError("func has to be implemented or _func_path has to be overwritten")

    @abstractmethod
    def _schedule(self):
        pass

    def handle(self, *args, **options):
        if options['schedule']:
            self._schedule()
            self.stdout.write("Created a schedule")
            return
        else:
            func = pydoc.locate(self._func_path())
            func()
