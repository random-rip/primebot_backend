import concurrent.futures
import logging
import threading

import requests

from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import EnemyNewTimeSuggestionsNotificationMessage, \
    OwnNewTimeSuggestionsNotificationMessage, ScheduleConfirmationNotification, NewLineupNotificationMessage
from comparing.game_comparer import GameMetaData, GameComparer
from utils.messages_logger import log_exception

thread_local = threading.local()
django_logger = logging.getLogger("django")
notifications_logger = logging.getLogger("notifications")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session

@log_exception
def check_game(game):
    game_id = game.game_id
    team = game.team_a
    gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, )
    cmp = GameComparer(game, gmd)

    log_message = f"New notification for {game_id} ({team}): "
    django_logger.debug(f"Checking {game_id} ({team})...")
    dispatcher = MessageDispatcher(team)
    if cmp.compare_new_suggestion(of_enemy_team=True):
        notifications_logger.debug(f"{log_message}Neuer Zeitvorschlag der Gegner")
        game.update_latest_suggestion(gmd)
        dispatcher.dispatch(EnemyNewTimeSuggestionsNotificationMessage, game=game)
    if cmp.compare_new_suggestion():
        notifications_logger.debug(f"{log_message}Eigener neuer Zeitvorschlag")
        game.update_latest_suggestion(gmd)
        dispatcher.dispatch(OwnNewTimeSuggestionsNotificationMessage, game=game)
    if cmp.compare_scheduling_confirmation():
        notifications_logger.debug(f"{log_message}Termin wurde festgelegt")
        game.update_game_begin(gmd)
        dispatcher.dispatch(ScheduleConfirmationNotification, game=game,
                            latest_confirmation_log=gmd.latest_confirmation_log)

    if cmp.compare_lineup_confirmation():
        notifications_logger.debug(f"{log_message}Neues Lineup des gegnerischen Teams")
        gmd.get_enemy_team_data()
        game.update_enemy_team(gmd)
        game.update_enemy_lineup(gmd)
        dispatcher.dispatch(NewLineupNotificationMessage, game=game)

    game.update_from_gmd(gmd)


def update_uncompleted_games(games, use_concurrency=True):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(check_game, games)
    else:
        for i in games:
            check_game(game=i)
