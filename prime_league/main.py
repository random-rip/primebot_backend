from babel.dates import format_datetime
from telepot import Bot
import os
from api import get_website_of_match
from classes import Game, Comparer, LogSchedulingAutoConfirmation
from database import DatabaseConnector
from emoji_constants import EMOJI_ONE, EMOJI_TWO, EMOJI_THREE, EMOJI_ARROW, EMOJI_SUCCESS
from regex_operations import RegexOperator
from dotenv import load_dotenv

load_dotenv(os.path.join(os.getcwd(), '.env'))
database = DatabaseConnector()

bot = Bot(token=os.getenv("TELEGRAM_BOT_API_KEY"))

emoji_numbers = [EMOJI_ONE, EMOJI_TWO, EMOJI_THREE]


def main():
    check_uncompleted_games()


def check_uncompleted_games():
    """Checks games from db which are uncompleted """
    records = database.get_uncompleted_games_from_db()
    for record in records:
        old_game = Game.deserialize(record[1])
        game_id = old_game.game_id
        team_id = record[7]
        chat_id = record[6]
        website = get_website_of_match(game_id)
        game_day = RegexOperator.get_game_day(website)
        enemy_team_id = RegexOperator.get_enemy_team_id(website)
        enemy_team_name = RegexOperator.get_enemy_team_name(website)
        new_game = Game(game_id, RegexOperator.get_logs(website), game_day,
                        enemy_team_id)
        cmp = Comparer(old_game, new_game)
        if cmp.compare_new_suggestion_of_enemy():
            log = new_game.get_latest_suggestion_log(of_enemy=True)
            times = ""
            times = [format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de") for x in log.details]
            for i, val in enumerate(times):
                times[i] = emoji_numbers[i] + val
            prefix = "Neuer Zeitvorschlag" if len(times) == 1 else "Neue Zeitvorschläge"
            text = prefix + " von " + enemy_team_name + " für Spieltag " + game_day + ":\n" + "\n".join(times)
            text += "\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{}) zur Seite.".format(game_id)
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
        if cmp.compare_new_suggestion_of_our_team():
            text = "Neuer [Zeitvorschlag von uns](https://www.primeleague.gg/de/leagues/matches/{}) für Spieltag ".format(
                game_id) + \
                   game_day + " gegen " + enemy_team_name + ". " + EMOJI_SUCCESS
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
        if cmp.compare_scheduling_confirmation():
            log = new_game.get_scheduling_confirmation_log()
            if isinstance(log, LogSchedulingAutoConfirmation):
                text = "Das Team " + enemy_team_name + " hat für Spieltag " + game_day + " weder die vorgeschlagene Zeit angenommen, " + \
                       "noch eine andere vorgeschlagen. Damit ist der Spieltermin\n" + EMOJI_ARROW + \
                       format_datetime(log.details, "EEEE, d. MMM y H:mm'Uhr'", locale="de") + " bestätigt."
            else:
                text = "Spielbestätigung von " + enemy_team_name + " für Spieltag " + game_day + ":\n" + EMOJI_ARROW + \
                       format_datetime(log.details, "EEEE, d. MMM y H:mm'Uhr'", locale="de")
            text += "\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{}) zur Seite.".format(game_id)
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
        if cmp.compare_lineup_confirmation():
            op_link = new_game.create_op_link_of_enemy_lineup()
            text = enemy_team_name + " hat ein neues [Lineup]({}) aufgestellt.".format(op_link)
            bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")

        database.delete_game(game_id)
        query = "INSERT INTO prime_league (id, json, game_closed, game_day, enemy_team_id, chat_id, team_id) VALUES ({},'{}',{}, {},{}, {}, {})" \
            .format(game_id, new_game.serialize(), new_game.match_ended, game_day, enemy_team_id, chat_id, team_id)
        database.insert_to_db(query)


def _main():
    main()
    database.close_connection()


if __name__ == '__main__':
    _main()
