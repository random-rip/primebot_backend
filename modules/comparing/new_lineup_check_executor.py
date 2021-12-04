import concurrent.futures
import logging
import threading

import requests

from bots.message_dispatcher import MessageDispatcher
from bots.messages import NewLineupInCalibrationMessage
from modules.comparing.game_comparer import GameMetaData, GameComparer

thread_local = threading.local()
calibration_logger = logging.getLogger("calibration")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def check_match(match):
    game_id = match.game_id
    team = match.team
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    cmp = GameComparer(match, gmd)

    log_message = f"New notification for {game_id} ({team}): "
    calibration_logger.debug(f"Checking {game_id} ({team})...")
    dispatcher = MessageDispatcher(team)
    if cmp.compare_lineup_confirmation():
        calibration_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        gmd.get_enemy_team_data()
        match.update_enemy_team(gmd)
        match.update_enemy_lineup(gmd)
        dispatcher.dispatch(NewLineupInCalibrationMessage, game=match, )

    match.update_from_gmd(gmd)


def check(uncompleted_games):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_match, uncompleted_games)
