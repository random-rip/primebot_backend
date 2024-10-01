import concurrent.futures
import logging
import sys
import traceback
from typing import Union

from django.conf import settings

from app_prime_league.models import Match, Player, Suggestion, Team
from bots.telegram_interface.tg_singleton import send_message_to_devs
from core.processors.team_processor import TeamDataProcessor
from core.providers.request_queue_processor import RequestQueueProvider
from core.temporary_match_data import TemporaryMatchData
from utils.messages_logger import log_exception


def register_team(*, team_id: int, **kwargs) -> Union[Team, None]:
    """
    This Function should be used in Bot commands!
    Add or Update a Team, Add or Update Matches.
    **kwargs will be directly parsed to the Team model, usually the telegram ID or discord IDs.
    :raises PrimeLeagueConnectionException, TeamWebsite404Exception:
    """
    processor = TeamDataProcessor(team_id=team_id, provider=RequestQueueProvider(priority=0, force=True))
    team = create_or_update_team(processor=processor, **kwargs)
    if team is None:
        return None
    try:
        create_matches(processor.get_matches(), team, use_concurrency=False)  # TODO speedup again?
    except Exception as e:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        send_message_to_devs(
            msg=f"Ein Fehler ist beim Registrieren von Team {team_id} aufgetreten.",
            code=f"{trace}\n{e}",
        )
        logging.getLogger("commands").exception(e)
    return team


def create_or_update_team(*, processor, **kwargs) -> Union[Team, None]:
    """
    Create or Update a Team. If team has matches and there is a current split the split will be set, else None.
    :param processor: processor object
    :param kwargs: kwargs for team model
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
    defaults = {**defaults, **kwargs}

    team, created = Team.objects.update_or_create(id=processor.team_id, defaults=defaults)
    return team


@log_exception
def create_match_and_enemy_team(team: Team, match_id: int):
    """
    Create Match, Enemy Team, Enemy Players, Enemy Lineup, Suggestions and Comments.
    :param team: Primary Team of the match
    :param match_id: Match ID
    """
    tmd = TemporaryMatchData.create_from_website(
        team=team, match_id=match_id, provider=RequestQueueProvider(priority=0)
    )
    match, created = Match.objects.update_or_create(
        match_id=match_id,
        team=team,
        defaults={
            "match_id": tmd.match_id,
            "match_day": tmd.match_day,
            "match_type": tmd.match_type,
            "team": tmd.team,
            "begin": tmd.begin,
            "team_made_latest_suggestion": tmd.team_made_latest_suggestion,
            "match_begin_confirmed": tmd.match_begin_confirmed,
            "datetime_until_auto_confirmation": tmd.datetime_until_auto_confirmation,
            "closed": tmd.closed,
            "result": tmd.result,
            "has_side_choice": tmd.has_side_choice,
            "split": tmd.split,
        },
    )

    # Create Team Lineup
    if tmd.team_lineup is not None:
        players = Player.objects.create_or_update_players(tmd.team_lineup, team=team)
        match.team_lineup.add(*players)

    # Create Enemy Team
    if tmd.enemy_team_id is not None:
        processor = TeamDataProcessor(
            team_id=tmd.enemy_team_id,
            provider=RequestQueueProvider(priority=0),
        )  # TODO duplicate code
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

        # Create Enemy Players
        Player.objects.remove_old_player_relations(processor.get_members(), team)
        Player.objects.create_or_update_players(processor.get_members(), enemy_team)

    # Create Enemy Lineup
    # TODO: duplicate code, refactor to use match.update_enemy_lineup(md=tmd)
    match.update_enemy_lineup(md=tmd)
    if tmd.enemy_lineup is not None:
        match.enemy_lineup.clear()
        players = Player.objects.filter(id__in=[x[0] for x in tmd.enemy_lineup])
        match.enemy_lineup.add(*players)

    # Create Suggestions
    # TODO: duplicate code, refactor to use match.update_latest_suggestions(md=tmd)
    if tmd.latest_suggestions is not None:
        match.suggestion_set.all().delete()
        for suggestion in tmd.latest_suggestions:
            match.suggestion_set.add(Suggestion(match=match, begin=suggestion), bulk=False)
    match.team_made_latest_suggestion = match.team_made_latest_suggestion

    # Create Comments
    match.update_comments(tmd)

    match.save()


def create_matches(match_ids: list[int], team: Team, use_concurrency=not settings.DEBUG):
    """
    Used for registering new teams. Can be parallelized with threads if ``use_concurrency`` is True.
    :param match_ids: List of match ids
    :param team: Primary Team of the matches
    :param use_concurrency: if True use threads to parallelize every match
    """
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: create_match_and_enemy_team(*p), ((team, match_id) for match_id in match_ids))
        return

    for i in match_ids:
        create_match_and_enemy_team(team, match_id=i)
