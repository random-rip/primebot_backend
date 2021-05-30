import logging
import sys
import time
import traceback
from datetime import datetime

from telegram import ParseMode

from app_prime_league.models import Team, Game
from app_prime_league.teams import add_games
from communication_interfaces.message_dispatcher import MessageDispatcher
from communication_interfaces.messages import NewGameNotification
from communication_interfaces.telegram_interface.tg_singleton import send_message
from comparing.new_lineup_check_executor import check
from parsing.parser import TeamWrapper, WebsiteIsNoneException
from prime_league_bot import settings


def main():
    start_time = time.time()
    logger = logging.getLogger("calibration_logger")
    logger.info(f"Starting Team Updates at {datetime.now()}")
    teams = Team.objects.get_calibration_teams()

    for team in teams:
        logger.info(f"Checking {team}... ")
        try:
            parser = TeamWrapper(team_id=team.id).parser
        except WebsiteIsNoneException as e:
            logger.info(f"{e}, Skipping!")
            continue

        try:
            if team.is_active():
                game_ids = parser.get_matches()
                game_ids = [int(i) for i in game_ids]
                existing_games = list(team.games_against.all().values_list("game_id", flat=True))
                new_games = list(set(game_ids) - set(existing_games))
                add_games(new_games, team, ignore_lineup=True)
                if len(new_games):
                    next_game = team.get_next_open_game()
                    if next_game is not None:
                        MessageDispatcher(team=team).dispatch(NewGameNotification, game=next_game)
        except Exception as e:
            trace = "".join(traceback.format_tb(sys.exc_info()[2]))
            send_message(
                f"Ein Fehler ist beim Kalibrierungsphase-Script von Team {team.id} {team.name} aufgetreten:\n"
                f"<code>{trace}\n{e}</code>",
                chat_id=settings.TG_DEVELOPER_GROUP, parse_mode=ParseMode.HTML)
            logger.error(e)
    check(Game.objects.get_uncompleted_games())
    logger.info(f"Finished Teamupdates ({len(teams)}) in {time.time() - start_time} seconds")


def run():
    main()
