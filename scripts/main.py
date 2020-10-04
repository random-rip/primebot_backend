import concurrent.futures
import logging
import threading
import time
from datetime import datetime

import requests

from app_prime_league.models import Game
from communication_interfaces.telegram_interface.tg_singleton import TelegramMessagesWrapper
from comparing.game_comparer import GameMetaData, GameComparer

thread_local = threading.local()
main_logger = logging.getLogger("main_logger")
notifications_logger = logging.getLogger("notifications_logger")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def check_match(match):
    game_id = match.game_id
    team = match.team
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    cmp = GameComparer(match, gmd)
    settings = team.settings_dict()

    log_message = f"New notification for {game_id} ({team}): "
    main_logger.debug(f"Checking {game_id} ({team})...")
    if match.game_begin is None:
        if cmp.compare_new_suggestion(of_enemy_team=True):
            notifications_logger.debug(f"{log_message}Neuer Zeitvorschlag der Gegner")
            match.update_latest_suggestion(gmd)
            if settings.get("scheduling_suggestion", True):
                TelegramMessagesWrapper.send_new_suggestion_of_enemies(match)
        if cmp.compare_new_suggestion():
            notifications_logger.debug(f"{log_message}Eigener neuer Zeitvorschlag")
            match.update_latest_suggestion(gmd)
            if settings.get("scheduling_suggestion", True):
                TelegramMessagesWrapper.send_new_suggestion(match)
    if cmp.compare_scheduling_confirmation():
        notifications_logger.debug(f"{log_message}Termin wurde festgelegt")
        match.update_game_begin(gmd)
        if settings.get("scheduling_confirmation", True):
            TelegramMessagesWrapper.send_scheduling_confirmation(match, gmd.latest_confirmation_log)
    if cmp.compare_lineup_confirmation():
        notifications_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        gmd.get_enemy_team_data()
        match.update_enemy_team(gmd)
        match.update_enemy_lineup(gmd)
        if settings.get("lineup_op_link", True):
            TelegramMessagesWrapper.send_new_lineup_of_enemies(match)

    match.update_from_gmd(gmd)


def check(uncompleted_games):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_match, uncompleted_games)


def run():
    start_time = time.time()
    uncompleted_games = Game.objects.get_uncompleted_games()
    main_logger.info(f"Checking uncompleted games at {datetime.now()}...")
    check(uncompleted_games=uncompleted_games)

    main_logger.info(f"Checked uncompleted games ({len(uncompleted_games)}) in {time.time() - start_time} seconds")
