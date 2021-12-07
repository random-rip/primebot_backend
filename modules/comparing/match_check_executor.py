import concurrent.futures
import logging
import threading

import requests

from bots.message_dispatcher import MessageDispatcher
from bots.messages import EnemyNewTimeSuggestionsNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, ScheduleConfirmationNotification, NewLineupNotificationMessage
from modules.comparing.match_comparer import MatchComparer, PrimeLeagueMatchData
from utils.messages_logger import log_exception

thread_local = threading.local()
django_logger = logging.getLogger("django")
notifications_logger = logging.getLogger("notifications")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


@log_exception
def check_match(match):
    match_id = match.match_id
    team = match.team
    try:
        gmd = PrimeLeagueMatchData.create_from_website(team=team, match_id=match_id, )
    except Exception as e:
        django_logger.exception(e)
        return
    cmp = MatchComparer(match, gmd)

    log_message = f"New notification for {match_id} ({team}): "
    django_logger.debug(f"Checking {match_id} ({team})...")
    dispatcher = MessageDispatcher(team)
    if cmp.compare_new_suggestion(of_enemy_team=True):
        notifications_logger.debug(f"{log_message}Neuer Zeitvorschlag der Gegner")
        match.update_latest_suggestion(gmd)
        dispatcher.dispatch(EnemyNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_new_suggestion():
        notifications_logger.debug(f"{log_message}Eigener neuer Zeitvorschlag")
        match.update_latest_suggestion(gmd)
        dispatcher.dispatch(OwnNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_scheduling_confirmation():
        notifications_logger.debug(f"{log_message}Termin wurde festgelegt")
        match.update_match_begin(gmd)
        dispatcher.dispatch(ScheduleConfirmationNotification, match=match,
                            latest_confirmation_log=gmd.latest_confirmation_log)

    if cmp.compare_lineup_confirmation():
        notifications_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        gmd.get_enemy_team_data()
        match.update_enemy_team(gmd)
        match.update_enemy_lineup(gmd)
        dispatcher.dispatch(NewLineupNotificationMessage, match=match)

    match.update_from_gmd(gmd)


def update_uncompleted_matches(matches, use_concurrency=True):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(check_match, matches)
    else:
        for i in matches:
            check_match(match=i)
