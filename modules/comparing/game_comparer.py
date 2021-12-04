from typing import Union

from app_prime_league.models import Game, GameMetaData


class GameComparer:

    def __init__(self, game_old: Union[Game,], game_new: GameMetaData, ):
        self.game_old = game_old
        self.game_new = game_new

    def compare_new_suggestion(self, of_enemy_team=False):
        """
        Comparing a the latest suggestions of game_old and game_new and returns True if a new suggestion was made.
        If of_enemy_team is True, checks if the new suggestion was made by the enemy team.
        :param of_enemy_team:
        :return boolean: True if new suggestion else False
        """
        if self.game_new.latest_suggestion is None:
            return False

        new_suggestion_user = self.game_new.latest_suggestion.user
        old_suggestion = self.game_old.get_first_suggested_game_begin
        team_leaders = list(self.game_old.team.player_set.all().filter(is_leader=True).values_list("name", flat=True))
        if old_suggestion is not None and old_suggestion == self.game_new.latest_suggestion.details[0]:
            return False
        if (of_enemy_team and new_suggestion_user not in team_leaders) or \
                (not of_enemy_team and new_suggestion_user in team_leaders):
            return True
        return False

    def compare_scheduling_confirmation(self):
        return True if self.game_old.game_begin is None and self.game_new.game_begin is not None else False

    def compare_lineup_confirmation(self):
        if self.game_new.enemy_lineup is None:
            return False
        old_lineup = list(self.game_old.enemy_lineup.all().values_list("id", flat=True))

        new_lineup = [int(x[0]) for x in self.game_new.enemy_lineup]
        for i in new_lineup:
            if i in old_lineup:
                continue
            else:
                return True
        return False

    def compare_game_played(self):
        if not self.game_old.game_closed and self.game_new.game_closed:
            return True
        return False
