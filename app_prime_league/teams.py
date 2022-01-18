import concurrent.futures
import logging
import sys
import traceback

from telegram import ParseMode

from app_prime_league.models import Team, Player, Match
from bots import send_message
from modules.comparing.match_comparer import PrimeLeagueMatchData
from modules.processors.team_processor import TeamDataProcessor
from prime_league_bot import settings
from utils.exceptions import GMDNotInitialisedException
from utils.messages_logger import log_exception

logger = logging.getLogger("django")


def register_team(*, team_id, **kwargs):
    """
    This Function should be used in Bot commands!
    Add or Update a Team, Add or Update Players, Add or Update Matches.
    **kwargs will be directly parsed to the Team model.
    :raises PrimeLeagueConnectionException, TeamWebsite404Exception
    """
    team, provider = add_or_update_team(team_id=team_id, **kwargs)
    if team is not None:
        if team.division is not None:
            try:
                add_or_update_players(provider.get_members(), team)
                add_matches(provider.get_matches(), team, use_concurrency=True)
            except Exception as e:
                trace = "".join(traceback.format_tb(sys.exc_info()[2]))
                send_message(
                    f"Ein Fehler ist beim Updaten von Team {team.id} {team.name} aufgetreten:\n<code>{trace}\n{e}</code>",
                    chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
                logger.exception(e)

        return team
    else:
        return None


def add_or_update_team(*, team_id, **kwargs):
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

    team, created = Team.objects.get_or_create(id=team_id, defaults=defaults)
    if not created:
        Team.objects.filter(id=team.id).update(**kwargs)
        team = update_team(processor, team_id)
        team.save()
    return team, processor


def update_team(processor: TeamDataProcessor, team_id: int):
    name = processor.get_team_name()
    logo = processor.get_logo()
    team_tag = processor.get_team_tag()
    division = processor.get_current_division()

    team = Team.objects.filter(id=team_id, name=name, logo_url=logo, team_tag=team_tag, division=division)
    if team.exists():
        return team.first()
    try:
        team = Team.objects.get(id=team_id)
    except Team.DoesNotExist as e:
        return None
    logger.debug(f"Updating {team}...")
    team.name = name
    team.logo_url = logo
    team.team_tag = team_tag
    team.division = division
    team.save()
    return team


def add_or_update_players(members, team: Team):
    for (id_, name, summoner_name, is_leader,) in members:
        player = Player.objects.filter(id=id_, name=name, summoner_name=summoner_name, is_leader=is_leader).first()
        logger.debug(f"Updating {player}...")
        player, created = Player.objects.get_or_create(id=id_, defaults={
            "name": name,
            "team": team,
            "summoner_name": summoner_name,
            "is_leader": is_leader,
        })
        if not created:
            player.name = name
            player.is_leader = is_leader
            player.summoner_name = summoner_name
            player.save()


@log_exception
def add_match(team, match_id, ):
    gmd = PrimeLeagueMatchData.create_from_website(team=team, match_id=match_id, )
    match = Match.objects.get_match_of_team(match_id=match_id, team=team)
    logging.debug(f"Adding Match {match_id} ...")

    if match is None:
        match = Match()

    match.update_match_data(gmd)

    try:
        match.update_enemy_team(gmd)
        logging.debug(f"Added enemy Team of {match=}.")
    except GMDNotInitialisedException:
        logging.debug(f"Enemy Team of {match=} already in database, skipped.")

    match.update_enemy_lineup(gmd)
    match.update_latest_suggestion(gmd)


def add_matches(match_ids, team: Team, use_concurrency=True):
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
            executor.map(lambda p: add_match(*p), ((team, match_id) for match_id in match_ids))
    else:
        for i in match_ids:
            add_match(team, match_id=i)


@log_exception
def add_raw_match(team, match_id):
    Match.objects.get_or_create(
        match_id=match_id,
        team=team,
    )


def add_raw_matches(match_ids, team: Team, use_concurrency=True):
    """
    Used for new Matches of registered teams (usually at beginning of the split and swiss starter matches).
    Args:
        match_ids:
        team:
        use_concurrency:

    Returns: None

    """
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: add_raw_match(*p), ((team, match_id) for match_id in match_ids))
        return
    else:
        for i in match_ids:
            add_raw_match(team, match_id=i)
