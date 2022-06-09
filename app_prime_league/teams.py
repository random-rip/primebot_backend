import concurrent.futures
import logging
import sys
import traceback

from app_prime_league.models import Team, Player, Match, Suggestion, Comment
from bots.telegram_interface.tg_singleton import send_message_to_devs
from modules.processors.team_processor import TeamDataProcessor
from modules.temporary_match_data import TemporaryMatchData
from prime_league_bot import settings
from utils.messages_logger import log_exception


def register_team(*, team_id, **kwargs):
    """
    This Function should be used in Bot commands!
    Add or Update a Team, Add or Update Matches.
    **kwargs will be directly parsed to the Team model. Usually telegram ID or discord IDs
    :raises PrimeLeagueConnectionException, TeamWebsite404Exception
    """
    team, provider = create_or_update_team(team_id=team_id, **kwargs)
    if team is None:
        return None
    try:
        create_matches(provider.get_matches(), team)

    except Exception as e:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        send_message_to_devs(
            f"Ein Fehler ist beim Registrieren von Team {team.id} {team.name} aufgetreten:\n<code>{trace}\n{e}</code>")
        logging.getLogger("commands").exception(e)
    return team


def create_or_update_team(*, team_id, **kwargs):
    """

    Args:
        team_id:
        **kwargs:

    Returns:
    Exceptions: PrimeLeagueConnectionException, TeamWebsite404Exception
    """
    processor = TeamDataProcessor(team_id=team_id)

    defaults = {
        "name": processor.get_team_name(),
        "team_tag": processor.get_team_tag(),
        "division": processor.get_current_division(),
        "logo_url": processor.get_logo(),
    }
    defaults = {**defaults, **kwargs}

    team, created = Team.objects.update_or_create(id=team_id, defaults=defaults)
    return team, processor


@log_exception
def create_match_and_enemy_team(team, match_id, ):
    """
    Create Match, Enemy Team, Enemy Players, Enemy Lineup, Suggestions
    Args:
        team:
        match_id:

    Returns:

    """
    # Create Match
    tmd = TemporaryMatchData.create_from_website(team=team, match_id=match_id, )
    match, created = Match.objects.update_or_create(match_id=match_id, team=team, defaults={
        "match_id": tmd.match_id,
        "match_day": tmd.match_day,
        "match_type": tmd.match_type,
        "team": tmd.team,
        "begin": tmd.begin,
        "team_made_latest_suggestion": tmd.team_made_latest_suggestion,
        "match_begin_confirmed": tmd.match_begin_confirmed,
        "closed": tmd.closed,
        "result": tmd.result,
        "has_side_choice": tmd.has_side_choice,
    })

    # Create Team Lineup
    if tmd.team_lineup is not None:
        players = Player.objects.create_or_update_players(tmd.team_lineup, team=team)
        match.team_lineup.add(*players)

    # Create Enemy Team
    processor = TeamDataProcessor(team_id=tmd.enemy_team_id)
    enemy_team, created = Team.objects.update_or_create(id=tmd.enemy_team_id, defaults={
        "name": processor.get_team_name(),
        "team_tag": processor.get_team_tag(),
        "division": processor.get_current_division(),
    })
    match.enemy_team = enemy_team

    # Create Enemy Players
    _ = Player.objects.create_or_update_players(processor.get_members(), enemy_team)

    # Create Enemy Lineup
    if tmd.enemy_lineup is not None:
        match.enemy_lineup.clear()
        players = Player.objects.filter(id__in=[x[0] for x in tmd.enemy_lineup])
        match.enemy_lineup.add(*players)

    # Create Suggestions
    if tmd.latest_suggestions is not None:
        match.suggestion_set.all().delete()
        for suggestion in tmd.latest_suggestions:
            match.suggestion_set.add(Suggestion(match=match, begin=suggestion), bulk=False)
    match.team_made_latest_suggestion = match.team_made_latest_suggestion

    # Create Comments
    for i in tmd.comments:
        Comment.objects.update_or_create(id=i.comment_id, defaults={**i.comment_as_dict(), "match": match})

    match.save()


def create_matches(match_ids, team: Team, use_concurrency=not settings.DEBUG):
    """
    Used for registering new teams.
    Args:
        match_ids:
        team:
        use_concurrency:

    Returns: None

    """
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: create_match_and_enemy_team(*p), ((team, match_id) for match_id in match_ids))
        return

    for i in match_ids:
        create_match_and_enemy_team(team, match_id=i)
