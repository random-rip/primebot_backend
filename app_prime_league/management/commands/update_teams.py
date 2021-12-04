import logging
import sys
import time
import traceback
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from telegram import ParseMode

from app_prime_league.models import Team
from app_prime_league.teams import update_team, add_or_update_players, add_raw_games
from bots import send_message
from modules.processors.team_processor import TeamDataProcessor
from utils.exceptions import PrimeLeagueConnectionException, TeamWebsite404Exception


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_time = time.time()
        logger = logging.getLogger("django")
        logger.debug(f"Starting Team Updates at {datetime.now()}")
        teams = Team.objects.all()

        for team in teams:
            logger.info(f"Checking {team}... ")
            try:
                processor = TeamDataProcessor(team.id)
            except (PrimeLeagueConnectionException, TeamWebsite404Exception) as e:
                logger.exception(e)
                continue

            update_team(processor, team_id=team.id)
            team.refresh_from_db()
            if team.division is not None:
                try:
                    add_or_update_players(processor.get_members(), team)
                    if team.is_active():
                        game_ids = processor.get_matches()
                        logger.debug(f"Checking {len(game_ids)} games for {team}... ")
                        add_raw_games(game_ids, team, use_concurrency=True)
                except Exception as e:
                    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
                    send_message(
                        f"Ein Fehler ist beim Updaten von Team {team.id} {team.name} aufgetreten:\n<code>{trace}\n{e}</code>",
                        chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
                    logger.exception(e)

        logger.info(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")
