import concurrent.futures
import logging
import sys
import traceback
from itertools import repeat

from django.conf import settings

from app_prime_league.models import Match, Team
from bots.telegram_interface.tg_singleton import send_message_to_devs
from core.processors.team_processor import TeamDataProcessor
from core.providers.get import get_provider
from core.updater.matches_check_executor import update_match
from utils.messages_logger import log_exception


def register_team(*, team_id: int) -> Team:
    """
    This Function should be used in Bot commands!
    Add or Update a Team, Add or Update Matches.
    :raises PrimeLeagueConnectionException, TeamWebsite404Exception:
    """
    processor = TeamDataProcessor(team_id=team_id, provider=get_provider(priority=0, force=True))
    team = create_or_update_team(processor=processor)
    try:
        create_matches(processor.get_matches(), team, notify=False, use_concurrency=False)  # TODO speedup again?
    except Exception as e:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        send_message_to_devs(
            msg=f"Ein Fehler ist beim Registrieren von Team {team_id} aufgetreten.",
            code=f"{trace}\n{e}",
        )
        logging.getLogger("commands").exception(e)
    return team


def create_or_update_team(*, processor) -> Team:
    """
    Create or Update a Team. If team has matches and there is a current split the split will be set, else None.
    :param processor: processor object
    :return: team or None
    :raises: PrimeLeagueConnectionException, TeamWebsite404Exception
    """
    defaults = {
        "name": processor.get_team_name(),
        "team_tag": processor.get_team_tag(),
        "division": processor.get_current_division(),
        "logo_url": processor.get_logo(),
        "split": processor.get_split(),
    }

    team, created = Team.objects.update_or_create(id=processor.team_id, defaults=defaults)

    return team


@log_exception
def create_match_and_enemy_team(team: Team, match_id: int, notify):
    """
    Create Match, Enemy Team, Enemy Players, Enemy Lineup, Suggestions and Comments.
    :param team: Primary Team of the match
    :param match_id: Match ID
    :param notify: if True send notifications
    """
    match, created = Match.objects.get_or_create(
        match_id=match_id,
        team=team,
    )
    update_match(match, notify=notify, priority=0)


def create_matches(
    match_ids: list[int],
    team: Team,
    notify: bool,
    use_concurrency: bool = not settings.DEBUG,
):
    """
    Used for registering new teams. Can be parallelized with threads if ``use_concurrency`` is True.
    :param match_ids: List of match ids
    :param team: Primary Team of the matches
    :param notify: if True send notifications
    :param use_concurrency: if True use threads to parallelize every match
    """
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(
                create_match_and_enemy_team,
                repeat(team),
                match_ids,
                repeat(notify),
            )
        return

    for i in match_ids:
        create_match_and_enemy_team(team, match_id=i, notify=notify)
