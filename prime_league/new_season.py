import os

from telegram import Bot

from api import get_matches, get_website_of_match
from classes import Game
from database import DatabaseConnector
from regex_operations import RegexOperator

database = DatabaseConnector()


def main(team_id, chat_id):
    # response = requests.get(url_matches)
    # print(response.text)
    ids = RegexOperator.get_matches(get_matches(team_id))
    new_season(ids, chat_id, team_id)
    bot = Bot(token=os.getenv("TELEGRAM_BOT_API_KEY"))
    bot.sendMessage(chat_id=chat_id, text="Added Games for team {}".format(team_id), parse_mode="Markdown")


def new_season(ids, chat_id, team_id):
    for i in ids:
        website = get_website_of_match(i)
        game_day = RegexOperator.get_game_day(website)
        enemy_team_id = RegexOperator.get_enemy_team_id(website)
        game = Game(i, [], game_day,
                    enemy_team_id)
        dump = game.serialize()
        query = "INSERT INTO prime_league (id, json, game_closed, game_day, enemy_team_id, chat_id, team_id) VALUES ({},'{}',{}, {}, {}, {}, {})" \
            .format(i, dump, game.match_ended, game_day, enemy_team_id, chat_id, team_id)
        database.insert_to_db(query)


def _main():
    # team_id = sys.argv[1]
    # chat_id = sys.argv[2]
    for team_id, chat_id in [
        ("105959", "***REMOVED***"),
        ("105878", "-1001492173687"),
        ("93008", "-1001360890758"),
        ("111914", "-1001188217113"),
    ]:
        main(team_id, chat_id)
    database.close_connection()


if __name__ == '__main__':
    _main()
