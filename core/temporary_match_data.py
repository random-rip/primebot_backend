import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Union

from app_prime_league.models import Split, Team
from core.processors.match_processor import MatchDataProcessor
from core.processors.team_processor import TeamDataProcessor
from utils.exceptions import TeamWebsite404Exception
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
    def __init__(
        self,
        match_id=None,
        match_day=None,
        match_type=None,
        team=None,
        enemy_team_id=None,
        enemy_team=None,
        enemy_team_members=None,
        enemy_lineup=None,
        closed=None,
        result=None,
        team_made_latest_suggestion=None,
        latest_suggestions=None,
        begin=None,
        latest_confirmation_log=None,
        match_begin_confirmed=None,
        team_lineup=None,
        has_side_choice=None,
        comments=None,
        datetime_until_auto_confirmation=None,
        split=None,
    ):
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
        self.datetime_until_auto_confirmation: Union[datetime, None] = datetime_until_auto_confirmation
        self.has_side_choice = has_side_choice
        self.comments: list = comments or []
        self.split: Union[None, Split] = split

    def __repr__(self):
        return (
            f"MatchID: {self.match_id}"
            f"\nMatch day: {self.match_day},"
            f"\nMatch type: {self.match_type},"
            f"\nSplit: {self.split},"
            f"\nTeam: {self.team},"
            f"\nEnemy team: {self.enemy_team},"
            f"\nEnemy lineup: {self.enemy_lineup},"
            f"\nMatch closed: {self.closed},"
            f"\nMatch result: {self.result}"
            f"\nteam_made_latest_suggestion: {self.team_made_latest_suggestion}"
            f"\nLatest Suggestion: {self.latest_suggestions},"
            f"\nSuggestion confirmed: {self.begin},"
            f"\nMatch Begin confirmed: {self.match_begin_confirmed},"
            f"\nDatetime Until auto confirmation: {self.datetime_until_auto_confirmation}, "
        )

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
    def create_from_website(team: Team, match_id: int) -> "TemporaryMatchData":
        """
        Method to initialize a TMD object from a MatchDataProcessor
        Args:
            team: Team
            match_id: integer

        Returns: Initialized TMD
        Raises: PrimeLeagueConnectionException, PrimeLeagueParseException, Match404Exception

        """

        tmd = TemporaryMatchData()
        processor = MatchDataProcessor(match_id, team.id)

        tmd.match_id = match_id
        tmd.match_day = processor.get_match_day()
        tmd.match_type = processor.get_match_type()
        tmd.team = team
        tmd.enemy_team_id = processor.get_enemy_team_id()
        tmd.enemy_lineup = processor.get_enemy_lineup()
        tmd.team_lineup = processor.get_team_lineup()
        tmd.closed = processor.get_match_closed()
        tmd.team_made_latest_suggestion = processor.get_team_made_latest_suggestion()
        tmd.latest_suggestions = processor.get_latest_suggestions()
        tmd.begin = processor.get_match_begin()
        tmd.match_begin_confirmed = processor.get_match_begin_confirmed()
        tmd.datetime_until_auto_confirmation = processor.get_datetime_until_auto_confirmation()
        tmd.latest_confirmation_log = processor.get_latest_match_begin_log()
        tmd.result = processor.get_match_result()
        tmd.has_side_choice = processor.has_side_choice()
        tmd.comments = TemporaryMatchData.create_temporary_comments(processor.get_comments())

        split = Split.objects.get_current_split()
        if split is not None and tmd.begin is not None:
            if split.in_range(tmd.begin):
                tmd.split = split
            else:
                logging.getLogger("updates").warning(f"Match {match_id=} is not in current split {split=}")

        if not Team.objects.filter(id=tmd.enemy_team_id).exists():
            tmd.create_enemy_team_data_from_website()
        return tmd

    def create_enemy_team_data_from_website(self):
        if self.enemy_team_id is None:
            return
        try:
            processor = TeamDataProcessor(team_id=self.enemy_team_id)
        except TeamWebsite404Exception:
            return
        self.enemy_team = {
            "name": processor.get_team_name(),
            "team_tag": processor.get_team_tag(),
            "division": processor.get_current_division(),
        }
        self.enemy_team_members = processor.get_members()
