import os
import sys

from telepot import Bot

from api import get_matches
from database import DatabaseConnector
from regex_operations import RegexOperator

database = DatabaseConnector()


def main(team_id, chat_id):
    database.get_games_from_db(team_id)
    ids = RegexOperator.get_matches(get_matches(team_id))
    delete_games(ids)
    bot = Bot(token=os.getenv("TELEGRAM_BOT_API_KEY"))
    bot.sendMessage(chat_id=chat_id, text="Deleted {} games of team {}".format(len(ids), team_id),
                    parse_mode="Markdown")


def delete_games(ids):
    # TODO
    pass


def _main():
    team_id = sys.argv[1]
    main(team_id)
    database.close_connection()


if __name__ == '__main__':
    _main()
