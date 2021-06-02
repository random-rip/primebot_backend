import logging
import sys
import time
import traceback
from datetime import datetime

from telegram import ParseMode

from app_prime_league.models import Team
from app_prime_league.teams import add_or_update_players, update_team, add_raw_games
from communication_interfaces.telegram_interface.tg_singleton import send_message
from parsing.parser import TeamWrapper, WebsiteIsNoneException
from prime_league_bot import settings


def main():
    start_time = time.time()
    logger = logging.getLogger("django")
    logger.debug(f"Starting Team Updates at {datetime.now()}")
    teams = Team.objects.all()

    for team in teams:
        logger.info(f"Checking {team}... ")
        try:
            parser = TeamWrapper(team_id=team.id).parser
        except WebsiteIsNoneException as e:
            logger.info(f"{e}, Skipping!")
            continue

        update_team(parser, team_id=team.id)
        team.refresh_from_db()
        if team.division is not None:
            try:
                add_or_update_players(parser.get_members(), team)
                if team.is_active():
                    game_ids = parser.get_matches()
                    logger.debug(f"Checking {len(game_ids)} games for {team}... ")
                    add_raw_games(game_ids, team, use_concurrency=False)
            except Exception as e:
                trace = "".join(traceback.format_tb(sys.exc_info()[2]))
                send_message(
                    f"Ein Fehler ist beim Updaten von Team {team.id} {team.name} aufgetreten:\n<code>{trace}\n{e}</code>",
                    chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
                logger.error(e)

    logger.info(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")


def run():
    main()
