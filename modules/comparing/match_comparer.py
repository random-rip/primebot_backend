from typing import Union

from app_prime_league.models import Match, Team
from modules.processors.match_processor import MatchDataProcessor
from modules.processors.team_processor import TeamDataProcessor
from utils.exceptions import GMDNotInitialisedException


class PrimeLeagueMatchData:

    def __init__(self):
        self.match_id = None
        self.match_day = None
        self.team = None
        self.enemy_team = None
        self.enemy_lineup = None
        self.closed = None
        self.result = None
        self.latest_suggestion = None
        self.begin = None
        self.latest_confirmation_log = None

    def __repr__(self):
        return f"MatchID: {self.match_id}" \
               f"\nMatch day: {self.match_day}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemy team: {self.enemy_team}, " \
               f"\nEnemy lineup: {self.enemy_lineup}, " \
               f"\nMatch closed: {self.closed}, " \
               f"\nMatch result: {self.result}" \
               f"\nLatest Suggestion: {self.latest_suggestion}, " \
               f"\nSuggestion confirmed: {self.begin}, "

    def __str__(self):
        return self.__repr__()

    @staticmethod
    def create_from_website(team: Team, match_id):

        gmd = PrimeLeagueMatchData()
        processor = MatchDataProcessor(match_id, team.id)

        gmd.match_id = match_id
        gmd.match_day = processor.get_match_day()
        gmd.team = team
        gmd.enemy_team = {
            "id": processor.get_enemy_team_id(),
        }
        gmd.enemy_lineup = processor.get_enemy_lineup()
        if gmd.enemy_lineup is not None:
            enemy_tuples = []
            for i in gmd.enemy_lineup:
                enemy_tuples.append((*i,))
            gmd.enemy_lineup = enemy_tuples
        gmd.closed = processor.get_match_closed()
        gmd.latest_suggestion = processor.get_latest_suggestion()
        gmd.begin, gmd.latest_confirmation_log = processor.get_match_begin()
        gmd.result = processor.get_match_result()
        return gmd

    def get_enemy_team_data(self):
        if self.enemy_team is None:
            raise GMDNotInitialisedException("GMD is not initialized yet. Aborting...")
        processor = TeamDataProcessor(team_id=self.enemy_team["id"])
        self.enemy_team["members"] = processor.get_members()
        self.enemy_team["name"] = processor.get_team_name()
        self.enemy_team["tag"] = processor.get_team_tag()
        self.enemy_team["division"] = processor.get_current_division()


class MatchComparer:

    def __init__(self, match_old: Union[Match,], match_new: PrimeLeagueMatchData, ):
        self.match_old = match_old
        self.match_new = match_new

    def compare_new_suggestion(self, of_enemy_team=False):
        """
        Comparing a the latest suggestions of match_old and match_new and returns True if a new suggestion was made.
        If of_enemy_team is True, checks if the new suggestion was made by the enemy team.
        :param of_enemy_team:
        :return boolean: True if new suggestion else False
        """
        if self.match_new.latest_suggestion is None:
            return False

        new_suggestion_user = self.match_new.latest_suggestion.user_id
        old_suggestion = self.match_old.get_first_suggested_match_begin
        team_leaders = list(self.match_old.team.player_set.all().filter(is_leader=True).values_list("name", flat=True))
        if old_suggestion is not None and old_suggestion == self.match_new.latest_suggestion.details[0]:
            return False
        if (of_enemy_team and new_suggestion_user not in team_leaders) or \
                (not of_enemy_team and new_suggestion_user in team_leaders):
            return True
        return False

    def compare_scheduling_confirmation(self):
        return True if self.match_old.begin is None and self.match_new.begin is not None else False

    def compare_lineup_confirmation(self):
        if self.match_new.enemy_lineup is None:
            return False
        old_lineup = list(self.match_old.enemy_lineup.all().values_list("id", flat=True))

        new_lineup = self.match_new.enemy_lineup
        for i in new_lineup:
            if i in old_lineup:
                continue
            else:
                return True
        return False

    def compare_match_played(self):
        if not self.match_old.closed and self.match_new.closed:
            return True
        return False
