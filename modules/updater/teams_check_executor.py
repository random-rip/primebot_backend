import concurrent.futures
import logging
import sys
import traceback

from django.conf import settings

from app_prime_league.models import Team, Player
from app_prime_league.teams import create_matches
from bots.telegram_interface.tg_singleton import send_message_to_devs
from modules.processors.team_processor import TeamDataProcessor
from utils.messages_logger import log_exception

django_logger = logging.getLogger("django")


@log_exception
def update_team(team: Team):
    try:
        processor = TeamDataProcessor(team.id)
    except Exception as e:
        django_logger.exception(e)
        return

    to_update = {
        "name": processor.get_team_name(),
        "team_tag": processor.get_team_tag(),
        "division": processor.get_current_division(),
        "logo_url": processor.get_logo(),
    }

    if Team.objects.filter(id=team.id, **to_update).exists():
        return

    django_logger.debug(f"Updating {team}...")
    team.update(**to_update)

    Player.objects.create_or_update_players(processor.get_members(), team)

    if not team.is_active():
        return team

    try:
        new_match_ids = processor.get_matches()
        current_match_ids = team.matches_against.values_list("match_id", flat=True)
        missing_ids = list(set(new_match_ids) - set(current_match_ids))
        create_matches(missing_ids, team=team)

    except Exception as e:
        trace = "".join(traceback.format_tb(sys.exc_info()[2]))
        send_message_to_devs(
            msg=f"Ein Fehler ist beim Updaten der Matches von  Team {team.id} {team.name} aufgetreten:"
                f"\n<code>{trace}\n{e}</code>", )
        django_logger.exception(e)
    return team


def update_teams(teams, use_concurrency=not settings.DEBUG):
    if use_concurrency:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(update_team, teams)
    else:
        for i in teams:
            update_team(team=i)
