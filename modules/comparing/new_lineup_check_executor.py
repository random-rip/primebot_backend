import concurrent.futures
import logging
import threading

import requests

from bots.message_dispatcher import MessageDispatcher
from bots.messages import NewLineupInCalibrationMessage
from modules.comparing.match_comparer import MatchComparer, TemporaryMatchData

thread_local = threading.local()
calibration_logger = logging.getLogger("calibration")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


def check_calibration_match(match):
    match_id = match.match_id
    team = match.team
    gmd = TemporaryMatchData.create_from_website(team=team, match_id=match_id, )
    cmp = MatchComparer(match, gmd)

    log_message = f"New notification for {match_id} ({team}): "
    calibration_logger.debug(f"Checking {match_id} ({team})...")
    dispatcher = MessageDispatcher(team)
    if cmp.compare_lineup_confirmation():
        calibration_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        gmd.create_enemy_team_data_from_website()
        match.update_enemy_team(gmd)
        match.update_enemy_lineup(gmd)
        dispatcher.dispatch(NewLineupInCalibrationMessage, match=match, )

    match.update_match_data(gmd)


def check(uncompleted_matches):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(check_calibration_match, uncompleted_matches)
