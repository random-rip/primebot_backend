from dataclasses import dataclass, field

from app_prime_league.models import Team
from core.processors.match_processor import MatchDataProcessor
from core.processors.team_processor import TeamDataProcessor
from utils.exceptions import GMDNotInitialisedException
from utils.utils import timestamp_to_datetime


@dataclass
class TemporaryComment:
    comment_id: int
    comment_parent_id: int
    comment_time: int
    user_id: int
    comment_edit_user_id: int
    comment_flag_staff: bool
    comment_flag_official: bool
    content: str = field(default="")

    def comment_as_dict(self):
        return {
            "comment_parent_id": self.comment_parent_id,
            "content": self.content,
            "user_id": self.user_id,
            "comment_edit_user_id": self.comment_edit_user_id,
            "comment_flag_staff": self.comment_flag_staff,
            "comment_flag_official": self.comment_flag_official,
            "comment_time": self.comment_time_as_datetime,
        }

    @property
    def comment_time_as_datetime(self):
        return timestamp_to_datetime(self.comment_time)


class TemporaryMatchData:

    def __init__(self, match_id=None, match_day=None, match_type=None, team=None, enemy_team_id=None, enemy_team=None,
                 enemy_team_members=None, enemy_lineup=None, closed=None, result=None, team_made_latest_suggestion=None,
                 latest_suggestions=None, begin=None, latest_confirmation_log=None, match_begin_confirmed=None,
                 team_lineup=None, has_side_choice=None, comments=None):
        self.match_id = match_id
        self.match_day = match_day
        self.match_type = match_type
        self.team = team
        self.enemy_team_id = enemy_team_id
        self.enemy_team = enemy_team
        self.enemy_team_members = enemy_team_members
        self.enemy_lineup = enemy_lineup
        self.team_lineup = team_lineup
        self.closed = closed
        self.result = result
        self.team_made_latest_suggestion = team_made_latest_suggestion
        self.latest_suggestions = latest_suggestions
        self.begin = begin
        self.latest_confirmation_log = latest_confirmation_log
        self.match_begin_confirmed = match_begin_confirmed
        self.has_side_choice = has_side_choice
        self.comments = comments or []

    def __repr__(self):
        return f"MatchID: {self.match_id}" \
               f"\nMatch day: {self.match_day}, " \
               f"\nMatch type: {self.match_type}, " \
               f"\nTeam: {self.team}, " \
               f"\nEnemy team: {self.enemy_team}, " \
               f"\nEnemy lineup: {self.enemy_lineup}, " \
               f"\nMatch closed: {self.closed}, " \
               f"\nMatch result: {self.result}" \
               f"\nteam_made_latest_suggestion: {self.team_made_latest_suggestion}" \
               f"\nLatest Suggestion: {self.latest_suggestions}, " \
               f"\nSuggestion confirmed: {self.begin}, " \
               f"\nMatch Begin confirmed: {self.match_begin_confirmed}, "

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create_temporary_comments(cls, comment_list):
        comments = []
        for i in comment_list:
            comment = TemporaryComment(**i)
            comments.append(comment)
        return comments

    @staticmethod
    def create_from_website(team: Team, match_id, ) -> "TemporaryMatchData":
        """

        Args:
            team:
            match_id:

        Returns:
        Raises: PrimeLeagueConnectionException, PrimeLeagueParseException, Match404Exception

        """

        gmd = TemporaryMatchData()
        processor = MatchDataProcessor(match_id, team.id)

        gmd.match_id = match_id
        gmd.match_day = processor.get_match_day()
        gmd.match_type = processor.get_match_type()
        gmd.team = team
        gmd.enemy_team_id = processor.get_enemy_team_id()
        gmd.enemy_lineup = processor.get_enemy_lineup()
        gmd.team_lineup = processor.get_team_lineup()
        gmd.closed = processor.get_match_closed()
        gmd.team_made_latest_suggestion = processor.get_team_made_latest_suggestion()
        gmd.latest_suggestions = processor.get_latest_suggestions()
        gmd.begin = processor.get_match_begin()
        gmd.match_begin_confirmed = processor.get_match_begin_confirmed()
        gmd.latest_confirmation_log = processor.get_latest_match_begin_log()
        gmd.result = processor.get_match_result()
        gmd.has_side_choice = processor.has_side_choice()
        gmd.comments = TemporaryMatchData.create_temporary_comments(processor.get_comments())

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
