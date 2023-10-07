from typing import Callable

from django.core.management import BaseCommand

from app_prime_league.models import Team
from core.cluster_job import Job


class Command(BaseCommand):
    def handle(self, *args, **options):
        TestJob().enqueue()


def test():
    teams = Team.objects.all()
    for team in teams:
        print(team)


class TestJob(Job):
    def function_to_execute(self) -> Callable:
        return test

    __name__ = 'TestJob'
