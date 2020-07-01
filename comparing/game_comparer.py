from typing import Union

from app_prime_league.models import Team, Game, GameMetaData


class GameComparer:

    def __init__(self, game_old: Union[Game,], game_new: GameMetaData, save_if_new=True):
        self.game_old = game_old
        self.game_new = game_new

    def compare_new_suggestion(self, of_enemy_team=False):
        if self.game_new.latest_suggestion is None:
            return False

        user = self.game_new.latest_suggestion["user"]
        if user == self.game_old.objects.get_latest_suggestion_log().name:
            return False

        team_leaders = self.game_old.player_set.filter(is_leader=True).values("name", flat=True)
        if of_enemy_team and user in team_leaders:
            return False
        if not of_enemy_team and user not in team_leaders:
            return False
        return True

    def compare_scheduling_confirmation(self):
        return True if self.game_old is None and self.game_new.suggestion_confirmed else False

    def compare_lineup_confirmation(self):

        old_lineup = self.game_old.enemy_lineup.all()
        # TODO Playerobjects in Tuple oder dicts ändern

        new_lineup = self.game_new.enemy_lineup
        for i in new_lineup:
            if i in old_lineup:
                continue
            else:
                return True
        return False
