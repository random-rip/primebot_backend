from typing import Union

from app_prime_league.models import Match
from modules.temporary_match_data import TemporaryMatchData


class MatchComparer:

    def __init__(self, match_old: Union[Match,], match_new: TemporaryMatchData, ):
        self.match_old = match_old
        self.match_new = match_new

    def compare_new_suggestion(self, of_enemy_team=False):
        """
        Comparing the latest suggestions of match_old and match_new and returns True if a new suggestion was made.
        If of_enemy_team is True, checks if the new suggestion was made by the enemy team.
        :param of_enemy_team:
        :return boolean: True if new suggestion else False
        """
        if self.match_new.team_made_latest_suggestion is None or \
                self.match_old.team_made_latest_suggestion == self.match_new.team_made_latest_suggestion:
            return False
        if of_enemy_team and not self.match_new.team_made_latest_suggestion:
            return True
        if not of_enemy_team and self.match_new.team_made_latest_suggestion:
            return True
        return False

    def compare_scheduling_confirmation(self):
        return not self.match_old.match_begin_confirmed and self.match_new.match_begin_confirmed

    def compare_lineup_confirmation(self):
        if self.match_new.enemy_lineup is None:
            return False
        old_lineup = list(self.match_old.enemy_lineup.all().values_list("id", flat=True))

        new_lineup = self.match_new.enemy_lineup
        for (user_id, *_) in new_lineup:
            if user_id in old_lineup:
                continue
            else:
                return True
        return False

    def compare_match_played(self):
        if not self.match_old.closed and self.match_new.closed:
            return True
        return False
