import logging
import sys
import time
import traceback
from datetime import datetime

from telegram import ParseMode

from app_prime_league.models import Team, Match
from app_prime_league.teams import add_matches
from bots.message_dispatcher import MessageDispatcher
from bots.messages import NewMatchNotification
from bots.telegram_interface.tg_singleton import send_message
from modules.comparing.new_lineup_check_executor import check
from modules.processors.team_processor import TeamDataProcessor
from prime_league_bot import settings
from utils.exceptions import TeamWebsite404Exception, PrimeLeagueConnectionException


def main():
    start_time = time.time()
    logger = logging.getLogger("calibration")
    logger.info(f"Starting Team Updates at {datetime.now()}")
    teams = Team.objects.get_watched_teams()

    for team in teams:
        logger.info(f"Checking {team}... ")
        try:
            processor = TeamDataProcessor(team_id=team.id)
        except (PrimeLeagueConnectionException, TeamWebsite404Exception) as e:
            logger.exception(e)
            continue

        try:
            if team.is_active():
                match_ids = processor.get_matches()
                match_ids = [int(i) for i in match_ids]
                existing_matches = list(team.matches_against.all().values_list("match_id", flat=True))
                new_matches = list(set(match_ids) - set(existing_matches))
                add_matches(new_matches, team, ignore_lineup=True)
                if len(new_matches):
                    next_math = team.get_next_open_match()
                    if next_math is not None:
                        MessageDispatcher(team=team).dispatch(NewMatchNotification, match=next_math)
        except Exception as e:
            trace = "".join(traceback.format_tb(sys.exc_info()[2]))
            send_message(
                f"Ein Fehler ist beim Kalibrierungsphase-Script von Team {team.id} {team.name} aufgetreten:\n"
                f"<code>{trace}\n{e}</code>",
                chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
            logger.exception(e)
    check(Match.objects.get_uncompleted_matches())
    logger.info(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")


def run():
    main()
