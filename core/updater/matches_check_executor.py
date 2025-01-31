import concurrent.futures
import logging
import threading
from itertools import repeat

import niquests
from django.conf import settings

from app_prime_league.models import Match
from core.comparers.match_comparer import (
    LineupConfirmationComparer,
    MatchComparer,
    NewCommentsComparer,
    NewEnemyTeamComparer,
    NewSuggestionComparer,
    SchedulingConfirmationComparer,
)
from core.providers.get import get_provider
from core.temporary_match_data import TemporaryMatchData
from utils.exceptions import Match404Exception
from utils.messages_logger import log_exception

thread_local = threading.local()
update_logger = logging.getLogger("updates")
notifications_logger = logging.getLogger("notifications")


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = niquests.Session()
    return thread_local.session


@log_exception
def update_match(match: Match, notify=True, priority=2):
    """
    Checks if a match has new data on the website, updates the match accordingly and sends notifications.

    Checks if there

    - is a new enemy team. If so, the enemy team is updated or created and the players are updated.
    - are new suggestions (either own or enemy team). If so, a notification is sent.
    - is a new scheduling confirmation. If so, a notification is sent.
    - is a new lineup (either own or enemy team). If so, a notification is sent.
    - are new comments. If so, a notification is sent.

    :param match: Match that will be updated
    :param priority: Priority new data will be fetched.
    :param notify: If True, notifications will be sent.
    """
    try:
        tmd = TemporaryMatchData.create_from_website(
            team=match.team,
            match_id=match.match_id,
            provider=get_provider(priority=priority),
        )
    except Match404Exception as e:
        match.delete()
        update_logger.info(f"Match deleted {e}")
        return
    except Exception as e:
        update_logger.exception(e)
        return

    comparer = MatchComparer(
        match=match,
        tmd=tmd,
        comparers=[
            NewEnemyTeamComparer(match=match, tmd=tmd, priority=priority),
            NewSuggestionComparer(match=match, tmd=tmd, of_enemy_team=True),
            NewSuggestionComparer(match=match, tmd=tmd, of_enemy_team=False),
            SchedulingConfirmationComparer(match=match, tmd=tmd),
            LineupConfirmationComparer(match=match, tmd=tmd, of_enemy_team=True),
            LineupConfirmationComparer(match=match, tmd=tmd, of_enemy_team=False),  # GLOBALLY SILENCED
            NewCommentsComparer(match=match, tmd=tmd),
        ],
    )
    comparer.run()
    comparer.update()

    if not notify:
        notifications_logger.info(f"Match {match} updated, but notifications are disabled.")
        return

    comparer.notify()


def update_uncompleted_matches(matches, notify: bool, use_concurrency=not settings.DEBUG):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(update_match, matches, repeat(notify))
    else:
        for i in matches:
            update_match(match=i, notify=notify)
