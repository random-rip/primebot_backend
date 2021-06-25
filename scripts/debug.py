import time
from datetime import datetime

from app_prime_league.models import Game
from comparing.games_check_executor import update_uncompleted_games


def main():
    start_time = time.time()
    uncompleted_games = Game.objects.filter(id=1203)
    print(f"Checking uncompleted games at {datetime.now()}...")
    update_uncompleted_games(games=uncompleted_games, use_concurrency=False)
    print(f"Checked uncompleted games ({len(uncompleted_games)}) in {time.time() - start_time} seconds")


# python manage.py runscript debug
def run():
    main()
