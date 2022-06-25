import logging
import threading
import time
from datetime import datetime

from django.core.management import BaseCommand

from app_prime_league.models import Team
from core.updater.teams_check_executor import update_teams

thread_local = threading.local()
logger = logging.getLogger("updates")


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()
        teams = Team.objects.all()
        logger.info(f"Updating {len(teams)} teams...")
        update_teams(teams=teams, )
        logger.info(f"Updated {len(teams)} teams in {time.time() - start_time:.2f} seconds")
