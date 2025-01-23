import concurrent.futures
import logging
import sys
import threading
import traceback
from itertools import repeat

from django.conf import settings
from django.utils import timezone
from django_q.models import Schedule

from app_prime_league.models import Player, Team
from app_prime_league.teams import create_matches
from bots.message_dispatcher import MessageCreatorJob
from bots.messages import MatchesOverview
from bots.messages.team_deleted import TeamDeletedMessage
from bots.telegram_interface.tg_singleton import send_message_to_devs
from core.comparers.team_comparer import TeamComparer
from core.processors.team_processor import TeamDataProcessor
from core.providers.get import get_provider
from utils.exceptions import TeamWebsite404Exception
from utils.messages_logger import log_exception

thread_local = threading.local()
update_logger = logging.getLogger("updates")
notifications_logger = logging.getLogger("notifications")


def delete_team(team: Team):
    """scheduled function to delete a team"""
    try:
        team.delete()
    except Team.DoesNotExist:  # noqa
        # Team does not exist anymore
        pass


@log_exception
def update_team(team: Team, notify: bool):
    try:
        processor = TeamDataProcessor(team.id, provider=get_provider(priority=2))
    except TeamWebsite404Exception:
        if not team.is_registered():
            team.delete()
        else:
            MessageCreatorJob(
                msg_class=TeamDeletedMessage,
                team=team,
            ).enqueue()
            Schedule.objects.create(
                name=f"Delete team {team.id}",
                schedule_type=Schedule.ONCE,
                next_run=timezone.now() + timezone.timedelta(hours=1),
                func="core.updater.teams_check_executor.delete_team",
                args=team,
            )
        return
    except Exception as e:
        update_logger.exception(e)
        return

    to_update = {
        "name": processor.get_team_name(),
        "team_tag": processor.get_team_tag(),
        "division": processor.get_current_division(),
        "logo_url": processor.get_logo(),
        "split": processor.get_split(),
    }

    update_logger.info(f"Updating {team}...")
    team.update(**to_update)

    try:
        Player.objects.remove_old_player_relations(processor.get_members(), team)
        Player.objects.create_or_update_players(processor.get_members(), team)
    except Exception:
        update_logger.warning(
            f"Exception occurred while updating players on team {team}. Players: {processor.get_members()}"
        )
        # TODO Spieler ohne namen werden von der Prime League zurückgegeben, sollen die gespeichert werden?
        pass

    if not notify or not team.is_registered():
        return team

    try:
        cmp = TeamComparer(team, processor=processor)
        log_message = f"New notification for {team=}: "
        if missing_ids := cmp.compare_new_matches():
            notifications_logger.info(f"{log_message}Neue Matches")
            create_matches(missing_ids, team=team, notify=True, use_concurrency=False)
            MessageCreatorJob(msg_class=MatchesOverview, team=team, match_ids=missing_ids).enqueue()

    except Exception as e:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        send_message_to_devs(
            msg=f"Ein Fehler ist beim Updaten der Matches von Team {team.id} {team.name} aufgetreten.",
            code=f"{trace}\n{e}",
        )
        update_logger.exception(e)
    return team


def update_teams(teams, notify: bool, use_concurrency=not settings.DEBUG):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(update_team, teams, repeat(notify))
    else:
        for i in teams:
            update_team(team=i, notify=notify)
