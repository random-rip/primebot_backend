from app_prime_league.models import Game
from comparing.game_comparer import GameMetaData, GameComparer
from data_crawling.api import crawler


def run():
    # TODO: in threads auslagern
    uncompleted_games = Game.objects.get_uncompleted_games()
    # uncompleted_games = Game.objects.filter(game_id=597478)
    for i in uncompleted_games:
        print("Game ", i)
        game_id = i.game_id
        team = i.team
        website = crawler.get_match_website(i)
        gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id, website=website)
        cmp = GameComparer(i, gmd)
        if i.game_begin is None:
            if cmp.compare_new_suggestion(of_enemy_team=True):
                print("Neuer Zeitvorschlag der Gegner")
                i.update_latest_suggestion()
            if cmp.compare_new_suggestion():
                print("Eigener neuer Zeitvorschlag")
                i.update_latest_suggestion()
        if cmp.compare_scheduling_confirmation():
            print("Termin wurde festgelegt")
        if cmp.compare_lineup_confirmation():
            print("Neues Lineup des gegnerischen Teams")
            i.update_enemy_team(gmd)
            i.update_enemy_lineup(gmd)

        i.update_from_gmd(gmd)
