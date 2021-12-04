import logging
import threading
import time
from datetime import datetime

from app_prime_league.models import Game
from modules.comparing.games_check_executor import update_uncompleted_games

thread_local = threading.local()
logger = logging.getLogger("django")


def run():
    start_time = time.time()
    uncompleted_games = Game.objects.get_uncompleted_games()
    logger.info(f"Checking uncompleted games ({len(uncompleted_games)}) at {datetime.now()}...")
    update_uncompleted_games(games=uncompleted_games, use_concurrency=True)
    logger.info(f"Checked uncompleted games ({len(uncompleted_games)}) in {time.time() - start_time} seconds")
