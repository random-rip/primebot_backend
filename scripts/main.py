import time

from app_prime_league.models import Game
from comparing.game_comparer import GameMetaData, GameComparer
from telegram_interface.tg_singleton import TelegramMessagesWrapper


def run():
    start_time = time.time()
    uncompleted_games = Game.objects.get_uncompleted_games()
    for i in uncompleted_games:
        print("Game ", i)
        game_id = i.game_id
        team = i.team
        gmd = GameMetaData.create_game_meta_data_from_website(team=team, game_id=game_id,)
        cmp = GameComparer(i, gmd)
        if i.game_begin is None:
            if cmp.compare_new_suggestion(of_enemy_team=True):
                print("Neuer Zeitvorschlag der Gegner")
                i.update_latest_suggestion(gmd)
                TelegramMessagesWrapper.send_new_suggestion_of_enemies(i)
            if cmp.compare_new_suggestion():
                print("Eigener neuer Zeitvorschlag")
                i.update_latest_suggestion(gmd)
                TelegramMessagesWrapper.send_new_suggestion(i)
        if cmp.compare_scheduling_confirmation():
            print("Termin wurde festgelegt")
            i.update_game_begin(gmd)
            TelegramMessagesWrapper.send_scheduling_confirmation(i, gmd.auto_confirmation)
        if cmp.compare_lineup_confirmation():
            print("Neues Lineup des gegnerischen Teams")
            gmd.get_enemy_team_data()
            i.update_enemy_team(gmd)
            i.update_enemy_lineup(gmd)
            TelegramMessagesWrapper.send_new_lineup_of_enemies(i)

        i.update_from_gmd(gmd)

    duration = time.time() - start_time
    print(f"Check all {len(uncompleted_games)} in {duration} seconds")