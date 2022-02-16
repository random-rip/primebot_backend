import concurrent.futures
import logging
import threading

import requests
from django.conf import settings

from bots.message_dispatcher import MessageDispatcher
from bots.messages import EnemyNewTimeSuggestionsNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, ScheduleConfirmationNotification, NewLineupNotificationMessage
from modules.match_comparer import MatchComparer
from modules.temporary_match_data import TemporaryMatchData
from utils.messages_logger import log_exception

thread_local = threading.local()
update_logger = logging.getLogger("updates")
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
        gmd = TemporaryMatchData.create_from_website(team=team, match_id=match_id, )
    except Exception as e:
        update_logger.exception(e)
        return

    cmp = MatchComparer(match, gmd)
    # TODO: Nice to have: Eventuell nach einem comparing und updaten mit match.refresh_from_db() arbeiten
    log_message = f"New notification for {match_id=} ({team=}): "
    update_logger.debug(f"Checking {match_id=} ({team=})...")
    dispatcher = MessageDispatcher(team)
    if cmp.compare_new_suggestion(of_enemy_team=True):
        notifications_logger.debug(f"{log_message}Neuer Terminvorschlag der Gegner")
        match.update_latest_suggestions(gmd)
        dispatcher.dispatch(EnemyNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_new_suggestion():
        notifications_logger.debug(f"{log_message}Eigener neuer Terminvorschlag")
        match.update_latest_suggestions(gmd)
        dispatcher.dispatch(OwnNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_scheduling_confirmation():
        notifications_logger.debug(f"{log_message}Termin wurde festgelegt")
        match.update_match_begin(gmd)
        dispatcher.dispatch(ScheduleConfirmationNotification, match=match,
                            latest_confirmation_log=gmd.latest_confirmation_log)

    if cmp.compare_lineup_confirmation():
        notifications_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        match.update_enemy_lineup(gmd)
        dispatcher.dispatch(NewLineupNotificationMessage, match=match)

    match.update_match_data(gmd)


def update_uncompleted_matches(matches, use_concurrency=not settings.DEBUG):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(check_match, matches)
    else:
        for i in matches:
            check_match(match=i)
