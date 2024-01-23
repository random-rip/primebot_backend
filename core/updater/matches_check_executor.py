import concurrent.futures
import logging
import threading

import requests
from django.conf import settings

from app_prime_league.models import Match, Player, Team
from bots.message_dispatcher import MessageCollector
from bots.messages import (
    EnemyNewTimeSuggestionsNotificationMessage,
    NewCommentsNotificationMessage,
    NewLineupNotificationMessage,
    OwnNewTimeSuggestionsNotificationMessage,
    ScheduleConfirmationNotification,
)
from core.comparers.match_comparer import MatchComparer
from core.processors.team_processor import TeamDataProcessor
from core.temporary_match_data import TemporaryMatchData
from utils.exceptions import Match404Exception
from utils.messages_logger import log_exception

thread_local = threading.local()
update_logger = logging.getLogger("updates")
notifications_logger = logging.getLogger("notifications")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = requests.Session()
    return thread_local.session


@log_exception
def check_match(match: Match):
    """
    Checks if a match has new data on the website, updates the match accordingly and sends notifications.

    Checks if there

    - is a new enemy team. If so, the enemy team is updated or created and the players are updated.
    - are new suggestions (either own or enemy team). If so, a notification is sent.
    - is a new scheduling confirmation. If so, a notification is sent.
    - is a new lineup (either own or enemy team). If so, a notification is sent.
    - are new comments. If so, a notification is sent.

    :param match: Match that will be updated
    """
    match_id = match.match_id
    team = match.team
    try:
        tmd = TemporaryMatchData.create_from_website(team=team, match_id=match_id)
    except Match404Exception as e:
        match.delete()
        update_logger.info(f"Match deleted {e}")
        return
    except Exception as e:
        update_logger.exception(e)
        return

    cmp = MatchComparer(match, tmd)
    # TODO: Nice to have: Eventuell nach einem comparing und updaten mit match.refresh_from_db() arbeiten
    log_message = f"New notification for {match_id=} ({team=}): "
    update_logger.info(f"Checking {match_id=} ({team=})...")
    collector = MessageCollector(team)
    if cmp.compare_new_enemy_team():
        processor = TeamDataProcessor(team_id=tmd.enemy_team_id)
        enemy_team, created = Team.objects.update_or_create(
            id=tmd.enemy_team_id,
            defaults={
                "name": processor.get_team_name(),
                "team_tag": processor.get_team_tag(),
                "division": processor.get_current_division(),
                "split": processor.get_split(),
            },
        )
        match.enemy_team = enemy_team
        Player.objects.remove_old_player_relations(processor.get_members(), team)
        Player.objects.create_or_update_players(processor.get_members(), enemy_team)
    if cmp.compare_new_suggestion(of_enemy_team=True):
        notifications_logger.info(f"{log_message}Neuer Terminvorschlag der Gegner")
        match.update_latest_suggestions(tmd)
        collector.dispatch(EnemyNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_new_suggestion():
        notifications_logger.info(f"{log_message}Eigener neuer Terminvorschlag")
        match.update_latest_suggestions(tmd)
        collector.dispatch(OwnNewTimeSuggestionsNotificationMessage, match=match)
    if cmp.compare_scheduling_confirmation():
        notifications_logger.info(f"{log_message}Termin wurde festgelegt")
        match.update_match_begin(tmd)
        collector.dispatch(
            ScheduleConfirmationNotification, match=match, latest_confirmation_log=tmd.latest_confirmation_log
        )
    if cmp.compare_lineup_confirmation(of_enemy_team=True):
        notifications_logger.info(f"{log_message}Neues Lineup des gegnerischen Teams")
        match.update_enemy_lineup(tmd)
        collector.dispatch(NewLineupNotificationMessage, match=match)
    if cmp.compare_lineup_confirmation(of_enemy_team=False):
        notifications_logger.info(f"Silenced notification for {match_id=} ({team=}): Neues eigenes Lineup")
        match.update_team_lineup(tmd)
    if comment_ids := cmp.compare_new_comments():
        notifications_logger.info(f"{log_message}Neue Kommentare: {comment_ids}")
        match.update_comments(tmd)
        collector.dispatch(NewCommentsNotificationMessage, match=match, new_comment_ids=comment_ids)

    match.update_match_data(tmd)


def update_uncompleted_matches(matches, use_concurrency=not settings.DEBUG):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(check_match, matches)
    else:
        for i in matches:
            check_match(match=i)
