from app_prime_league.models import Game
from comparing.game_comparer import GameMetaData, GameComparer
from data_crawling.api import Crawler


# def check_uncompleted_games():
#     """Checks games from db which are uncompleted """
#     records = database.get_uncompleted_games_from_db()
#     for record in records:
#         old_game = Game.deserialize(record[1])
#         game_id = old_game.game_id
#         team_id = record[7]
#         chat_id = record[6]
#         website = get_website_of_match(game_id)
#         game_day = RegexOperator.get_game_day(website)
#         enemy_team_id = RegexOperator.get_enemy_team_id(website)
#         enemy_team_name = RegexOperator.get_enemy_team_name(website)
#         new_game = Game(game_id, RegexOperator.get_logs(website), game_day,
#                         enemy_team_id)
#         cmp = Comparer(old_game, new_game)
#         if cmp.compare_new_suggestion_of_enemy():
#             log = new_game.get_latest_suggestion_log(of_enemy=True)
#             times = ""
#             times = [format_datetime(x, "EEEE, d. MMM y H:mm'Uhr'", locale="de") for x in log.details]
#             for i, val in enumerate(times):
#                 times[i] = emoji_numbers[i] + val
#             prefix = "Neuer Zeitvorschlag" if len(times) == 1 else "Neue Zeitvorschläge"
#             text = prefix + " von " + enemy_team_name + " für Spieltag " + game_day + ":\n" + "\n".join(times)
#             text += "\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{}) zur Seite.".format(game_id)
#             bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
#         if cmp.compare_new_suggestion_of_our_team():
#             text = "Neuer [Zeitvorschlag von uns](https://www.primeleague.gg/de/leagues/matches/{}) für Spieltag ".format(
#                 game_id) + \
#                    game_day + " gegen " + enemy_team_name + ". " + EMOJI_SUCCESS
#             bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
#         if cmp.compare_scheduling_confirmation():
#             log = new_game.get_scheduling_confirmation_log()
#             if isinstance(log, LogSchedulingAutoConfirmation):
#                 text = "Das Team " + enemy_team_name + " hat für Spieltag " + game_day + " weder die vorgeschlagene Zeit angenommen, " + \
#                        "noch eine andere vorgeschlagen. Damit ist der Spieltermin\n" + EMOJI_ARROW + \
#                        format_datetime(log.details, "EEEE, d. MMM y H:mm'Uhr'", locale="de") + " bestätigt."
#             else:
#                 text = "Spielbestätigung von " + enemy_team_name + " für Spieltag " + game_day + ":\n" + EMOJI_ARROW + \
#                        format_datetime(log.details, "EEEE, d. MMM y H:mm'Uhr'", locale="de")
#             text += "\nHier ist der [Link](https://www.primeleague.gg/de/leagues/matches/{}) zur Seite.".format(game_id)
#             bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
#         if cmp.compare_lineup_confirmation():
#             op_link = new_game.create_op_link_of_enemy_lineup()
#             text = enemy_team_name + " hat ein neues [Lineup]({}) aufgestellt.".format(op_link)
#             bot.sendMessage(chat_id=chat_id, text=text, parse_mode="Markdown")
#
#         database.delete_game(game_id)
#         query = "INSERT INTO prime_leagues (id, json, game_closed, game_day, enemy_team_id, chat_id, team_id) VALUES ({},'{}',{}, {},{}, {}, {})" \
#             .format(game_id, new_game.serialize(), new_game.match_ended, game_day, enemy_team_id, chat_id, team_id)
#         database.insert_to_db(query)


def run():
    # main()

    crawler = Crawler(local=False)
    # uncompleted_games = Game.objects.get_uncompleted_games()
    uncompleted_games = Game.objects.filter(game_id=597478)
    print(uncompleted_games)
    for i in uncompleted_games:
        print(i)
        game_id = i.game_id
        team_id = i.team.id
        website = crawler.get_match_website(i)
        gmd = GameMetaData.create_game_meta_data_from_website(team=team_id, game_id=game_id, website=website)
        cmp = GameComparer(i, gmd)
        if cmp.compare_new_suggestion(of_enemy_team=True):
            print("new suggestion")
