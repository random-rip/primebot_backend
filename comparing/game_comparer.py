from typing import Union

from app_prime_league.models import Team, Game
from parsing.regex_operations import HTMLParser


class GameMetaData:

    def __init__(self):
        self.game_id = None
        self.game_day = None
        self.team = None
        self.enemy_team = None
        self.enemy_lineup = None
        self.game_closed = None
        self.latest_suggestion = None
        self.suggestion_confirmed = None

    def __repr__(self):
        return f"GameID: {self.game_id}" \
               f"\nGameDay: {self.game_day}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemyTeam: {self.enemy_team}, " \
               f"\nEnemyLineup: {self.enemy_lineup}, " \
               f"\nGameClosed: {self.game_closed}, " \
               f"\nLatestSuggestion: {self.latest_suggestion}, " \
               f"\nSuggestionConfirmed: {self.suggestion_confirmed}, "

    @staticmethod
    def create_game_meta_data_from_website(team: Team, game_id, website, ):
        gmd = GameMetaData()
        parser = HTMLParser(website)

        gmd.game_id = game_id
        gmd.game_day = parser.get_game_day()
        gmd.team = team
        gmd.enemy_team = parser.get_enemy_team_id()
        gmd.enemy_lineup = parser.get_enemy_lineup()
        gmd.game_closed = parser.get_game_closed()
        gmd.latest_suggestion = parser.get_latest_suggestion()
        gmd.suggestion_confirmed = parser.get_suggestion_confirmed()

        return gmd


class GameComparer:

    def __init__(self, game_old: Union[None, Game], game_new: GameMetaData, save_if_new=True):
        self.game_old = game_old
        self.game_new = game_new

    def compare_new_suggestion_of_enemy(self):
        if self.game_new.latest_suggestion is None:
            return False

        user = self.game_new.latest_suggestion["user"]
        if user == self.game_old.objects.get_latest_suggestion_log().name:
            return False

        team_leaders = self.game_old.player_set.filter(is_leader=True).values("name", flat=True)
        if user in team_leaders:
            return False
        return True
    #
    # def compare_new_suggestion_of_our_team(self):
    #     if len(self.game_old.suggestion_logs) < len(self.game_new.suggestion_logs) and \
    #             len(self.game_new.suggestion_logs) > 0 and self.game_new.suggestion_logs[0].name \
    #             in TEAM_LEADER:
    #         return True
    #     return False
    #
    # def compare_scheduling_confirmation(self):
    #     old_log = self.game_old.get_scheduling_confirmation_log()
    #     new_log = self.game_new.get_scheduling_confirmation_log()
    #     if new_log is not None and old_log is None:
    #         return True
    #     return False
    #
    # def compare_lineup_confirmation(self):
    #     link_old = self.game_old.create_op_link_of_enemy_lineup()
    #     link_new = self.game_new.create_op_link_of_enemy_lineup()
    #     return True if link_old is None and link_new is not None else False
