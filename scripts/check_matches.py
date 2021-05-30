import logging
import threading
import time
from datetime import datetime

from app_prime_league.models import Game
from comparing.matches_check_executor import check

thread_local = threading.local()
main_logger = logging.getLogger("main_logger")
notifications_logger = logging.getLogger("notifications_logger")


def run():
    start_time = time.time()
    uncompleted_games = Game.objects.get_uncompleted_games()
    main_logger.info(f"Checking uncompleted games at {datetime.now()}...")
    check(uncompleted_games=uncompleted_games)

    main_logger.info(f"Checked uncompleted games ({len(uncompleted_games)}) in {time.time() - start_time} seconds")
