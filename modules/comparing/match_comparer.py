from typing import Union

from app_prime_league.models import Match, Team
from modules.processors.match_processor import MatchDataProcessor
from modules.processors.team_processor import TeamDataProcessor
from utils.exceptions import GMDNotInitialisedException


class TemporaryMatchData:

    def __init__(self, match_id=None, match_day=None, team=None, enemy_team_id=None, enemy_team=None,
                 enemy_team_members=None, enemy_lineup=None, closed=None, result=None, team_made_latest_suggestion=None,
                 latest_suggestions=None, begin=None, latest_confirmation_log=None, match_begin_confirmed=None):
        self.match_id = match_id
        self.match_day = match_day
        self.team = team
        self.enemy_team_id = enemy_team_id
        self.enemy_team = enemy_team
        self.enemy_team_members = enemy_team_members
        self.enemy_lineup = enemy_lineup
        self.closed = closed
        self.result = result
        self.team_made_latest_suggestion = team_made_latest_suggestion
        self.latest_suggestions = latest_suggestions
        self.begin = begin
        self.latest_confirmation_log = latest_confirmation_log
        self.match_begin_confirmed = match_begin_confirmed

    def __repr__(self):
        return f"MatchID: {self.match_id}" \
               f"\nMatch day: {self.match_day}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemy team: {self.enemy_team}, " \
               f"\nEnemy lineup: {self.enemy_lineup}, " \
               f"\nMatch closed: {self.closed}, " \
               f"\nMatch result: {self.result}" \
               f"\nLatest Suggestion: {self.latest_suggestions}, " \
               f"\nSuggestion confirmed: {self.begin}, "

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def create_from_website(team: Team, match_id, ) -> "TemporaryMatchData":

        gmd = TemporaryMatchData()
        processor = MatchDataProcessor(match_id, team.id)

        gmd.match_id = match_id
        gmd.match_day = processor.get_match_day()
        gmd.team = team
        gmd.enemy_team_id = processor.get_enemy_team_id()
        gmd.enemy_lineup = processor.get_enemy_lineup()
        if gmd.enemy_lineup is not None:
            enemy_tuples = []
            for i in gmd.enemy_lineup:
                enemy_tuples.append((*i,))
            gmd.enemy_lineup = enemy_tuples
        gmd.closed = processor.get_match_closed()
        gmd.team_made_latest_suggestion = processor.get_team_made_latest_suggestion()
        gmd.latest_suggestions = processor.get_latest_suggestions()
        gmd.begin = processor.get_match_begin()
        gmd.match_begin_confirmed = processor.get_match_begin_confirmed()
        gmd.latest_confirmation_log = processor.get_latest_match_begin_log()
        gmd.result = processor.get_match_result()

        if not Team.objects.filter(id=gmd.enemy_team_id).exists():
            gmd.create_enemy_team_data_from_website()
        return gmd

    def create_enemy_team_data_from_website(self):
        if self.enemy_team_id is None:
            raise GMDNotInitialisedException("GMD is not initialized yet. Aborting...")
        processor = TeamDataProcessor(team_id=self.enemy_team_id)
        self.enemy_team = {
            "name": processor.get_team_name(),
            "team_tag": processor.get_team_tag(),
            "division": processor.get_current_division(),
        }
        self.enemy_team_members = processor.get_members()


class MatchComparer:

    def __init__(self, match_old: Union[Match,], match_new: TemporaryMatchData, ):
        self.match_old = match_old
        self.match_new = match_new

    def compare_new_suggestion(self, of_enemy_team=False):
        """
        Comparing a the latest suggestions of match_old and match_new and returns True if a new suggestion was made.
        If of_enemy_team is True, checks if the new suggestion was made by the enemy team.
        :param of_enemy_team:
        :return boolean: True if new suggestion else False
        """
        if self.match_new.latest_suggestions is None or \
                self.match_old.team_made_latest_suggestion == self.match_new.team_made_latest_suggestion:
            return False
        if of_enemy_team and not self.match_new.team_made_latest_suggestion:
            return True
        if not of_enemy_team and self.match_new.team_made_latest_suggestion:
            return True
        return False

        # new_suggestion_user = self.match_new.latest_suggestion.user_id
        # old_suggestion = self.match_old.get_first_suggested_match_begin
        # team_leaders = list(self.match_old.team.player_set.all().filter(is_leader=True).values_list("name", flat=True))
        # if old_suggestion is not None and old_suggestion == self.match_new.latest_suggestion.details[0]:
        #     return False
        # if (of_enemy_team and new_suggestion_user not in team_leaders) or \
        #         (not of_enemy_team and new_suggestion_user in team_leaders):
        #     return True
        # return False

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
