import concurrent.futures
import threading
import time

import requests

from app_prime_league.models import Game
from comparing.game_comparer import GameMetaData, GameComparer
from telegram_interface.tg_singleton import TelegramMessagesWrapper

thread_local = threading.local()


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def check_match(match):
    print("Game ", match)
    game_id = match.game_id
    team = match.team
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    cmp = GameComparer(match, gmd)
    if match.game_begin is None:
        if cmp.compare_new_suggestion(of_enemy_team=True):
            print("Neuer Zeitvorschlag der Gegner")
            match.update_latest_suggestion(gmd)
            TelegramMessagesWrapper.send_new_suggestion_of_enemies(match)
        if cmp.compare_new_suggestion():
            print("Eigener neuer Zeitvorschlag")
            match.update_latest_suggestion(gmd)
            TelegramMessagesWrapper.send_new_suggestion(match)
    if cmp.compare_scheduling_confirmation():
        print("Termin wurde festgelegt")
        match.update_game_begin(gmd)
        TelegramMessagesWrapper.send_scheduling_confirmation(match, gmd.auto_confirmation)
    if cmp.compare_lineup_confirmation():
        print("Neues Lineup des gegnerischen Teams")
        gmd.get_enemy_team_data()
        match.update_enemy_team(gmd)
        match.update_enemy_lineup(gmd)
        TelegramMessagesWrapper.send_new_lineup_of_enemies(match)

    match.update_from_gmd(gmd)


def check(uncompleted_games):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_match, uncompleted_games)


def run():
    start_time = time.time()
    uncompleted_games = Game.objects.get_uncompleted_games()
    check(uncompleted_games=uncompleted_games)

    duration = time.time() - start_time
    print(f"Checked uncompleted games ({len(uncompleted_games)}) in {duration} seconds")
