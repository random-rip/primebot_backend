import logging
import threading
import time
from datetime import datetime

from django.core.management import BaseCommand

from app_prime_league.models import Match
from modules.updater.matches_check_executor import update_uncompleted_matches

thread_local = threading.local()
logger = logging.getLogger("updates")


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()
        uncompleted_matches = Match.objects.get_uncompleted_matches()
        logger.info(f"Checking {len(uncompleted_matches)} uncompleted matches...")
        update_uncompleted_matches(matches=uncompleted_matches)
        logger.info(f"Checked {len(uncompleted_matches)} uncompleted matches in {time.time() - start_time:.2f} seconds")
