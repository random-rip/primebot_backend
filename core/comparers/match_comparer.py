from typing import Union, List

from app_prime_league.models import Match
from core.temporary_match_data import TemporaryMatchData


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

    def compare_lineup_confirmation(self, of_enemy_team=False):
        new_lineup = self.match_new.enemy_lineup if of_enemy_team else self.match_new.team_lineup
        if new_lineup is None:
            return False
        old_lineup = self.match_old.enemy_lineup if of_enemy_team else self.match_old.team_lineup
        old_lineup = list(old_lineup.all().values_list("id", flat=True))
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

    def compare_new_comments(self) -> Union[List[int], bool]:
        """
        Check if new comments occurred which are not from team members.
        The list is sorted by comment_ids ascending.
        Returns: List of integers or False
        """
        user_ids_of_team = self.match_old.team.player_set.all().values_list("id", flat=True)
        old_comment_ids_without_team_comments = set(
            self.match_old.comment_set.exclude(user_id__in=user_ids_of_team).values_list("comment_id", flat=True))
        new_comment_ids_without_team_comments = set(
            [x.comment_id for x in self.match_new.comments if x.user_id not in user_ids_of_team])
        return sorted(list(new_comment_ids_without_team_comments - old_comment_ids_without_team_comments)) or False

    def compare_new_enemy_team(self):
        return not self.match_new.enemy_team_id == self.match_old.enemy_team_id
