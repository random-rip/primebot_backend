from datetime import datetime, time, timedelta
from typing import OrderedDict, Union

import pytz
from django.db import models
from django.utils.datetime_safe import datetime as datetime_safe
from django.utils.timezone import make_aware

from app_prime_league.models import Comment, Match, Player, Split, Team
from core.temporary_match_data import TemporaryComment, TemporaryMatchData
from utils.utils import timestamp_to_datetime


class CompareModelObjectsMixin:
    def assertModelObjectsListEqual(
        self, expected: list[Union[dict, object]], result: list[Union[dict, object]]
    ) -> None:
        """
        Compares a list of objects with another list of objects. If the objects are not of type `dict` or `OrderedDict`
        type, `dict(instance)` is used. If it is a model instance, `.__dict__` is used. If a key is not present in an
        object of the expected list, it is ignored. For example this is good for excluding created_at and updated_at
        fields in comparison.
        :param expected: The expected list of objects. Keys that are not present in the objects of this list are
            ignored.
        :param result: The actual result list of objects.

        **Examples**:
            >>> self.assertModelObjectsListEqual([{"a":1}, {"a":2}], [{"a":1}, {"a":3}]) # Fails
            Traceback (most recent call last):
            ...
            AssertionError:
            >>> self.assertModelObjectsListEqual([{"a":1}, {"a":2}], [{"a":1}, {"a":2}])
            None
            >>> self.assertModelObjectsListEqual([{"a":1}, {"a":2}], [{"a":1}, {"b":1}])
            None
        """
        self.assertEquals(len(expected), len(result))
        for n1, n2 in zip(expected, result):
            self.assertModelObjectEquals(n1, n2)

    def assertModelObjectEquals(
        self,
        expected: Union[dict, object],
        result: Union[dict, object],
    ) -> None:
        """
        Compares an object with another object. If the objects are not of type `dict` or `OrderedDict`
        type, `dict(instance)` is used. If it is a model instance, `.__dict__` is used. If a key is not present in the
        expected object, it is ignored. For example this is good for excluding created_at and updated_at fields in
        comparison.
        :param expected: The expected object. Keys that are not present in this object are ignored.
        :param result: The actual result object.
        **Examples**:
            >>> self.assertModelObjectEquals({"a":1, "b":2}, {"a":1, "b":3}) # Fails
            Traceback (most recent call last):
            ...
            AssertionError:
            >>> self.assertModelObjectEquals({"a":1}, {"a":1, "b":2}) # Succeeds because b is ignored
            None
            >>> self.assertModelObjectEquals({"a":1, "b":2}, {"a":1, "b":2})
            None
            >>> self.assertModelObjectEquals({"a":1, "b":2}, {"a":1, "c":1})
            None
        """

        d1, d2 = self.__compare(expected, result)
        self.assertEqual(len(d1), 0, f"\nExpected: {d1}\nActual result: {d2}")
        self.assertEqual(len(d2), 0, f"\nExpected: {d1}\nActual result: {d2}")

    def __to_dict(self, obj: Union[dict, list, object, None]) -> dict:
        try:
            return obj if type(obj) in (dict, OrderedDict) else dict(obj)
        except TypeError:  # Model instances
            return obj.__dict__
        except ValueError:
            raise AssertionError(f"Could not convert '{obj}' to dict.")

    def __is_assert_equal(self, obj_1, obj_2):
        return (
            (
                type(obj_1) not in [dict, OrderedDict, list]
                and type(obj_2) not in [dict, OrderedDict, list]
                and not issubclass(type(obj_1), models.Model)
                and not issubclass(type(obj_2), models.Model)
            )
            or obj_1 is None
            or obj_2 is None
        )

    def __is_list_equal(self, obj_1, obj_2):
        return type(obj_1) is list and type(obj_2) is list

    def __compare(
        self, obj_1: Union[dict, list, object, None], obj_2: Union[dict, list, object, None]
    ) -> tuple[dict, dict]:
        old = {}
        new = {}

        if self.__is_assert_equal(obj_1, obj_2):
            self.assertEqual(obj_1, obj_2)
            return old, new

        if self.__is_list_equal(obj_1, obj_2):
            self.assertModelObjectsListEqual(obj_1, obj_2)

        d1 = self.__to_dict(obj_1)
        d2 = self.__to_dict(obj_2)

        for k, v in d1.items():
            if type(v) is dict:
                try:
                    self.assertModelObjectEquals(v, d2[k])
                except AssertionError as e:
                    raise AssertionError(f"Dictionary comparison failed for key {k}:\n\t{e}")
                except KeyError:
                    old.update({k: v})
            elif type(v) is list:
                try:
                    self.assertModelObjectsListEqual(v, d2[k])
                except AssertionError as e:
                    raise AssertionError(f"List comparison failed for key {k}:\n\t{e}")
                except KeyError:
                    old.update({k: v})
            else:
                try:
                    if v != d2[k]:
                        old.update({k: v})
                        new.update({k: d2[k]})
                except KeyError:
                    old.update({k: v})

        return old, new


def string_to_datetime(x, timestamp_format='%Y-%m-%d %H:%M'):
    return datetime.strptime(x, timestamp_format).astimezone(pytz.utc)


def create_temporary_comment(
    comment_id=1,
    comment_parent_id=0,
    comment_time=1653986365,
    user_id=1,
    comment_edit_user_id=1,
    comment_flag_staff=False,
    comment_flag_official=False,
    content="",
):
    return TemporaryComment(
        comment_id=comment_id,
        comment_parent_id=comment_parent_id,
        comment_time=comment_time,
        user_id=user_id,
        comment_edit_user_id=comment_edit_user_id,
        comment_flag_staff=comment_flag_staff,
        comment_flag_official=comment_flag_official,
        content=content,
    )


def create_comment(
    match,
    comment_id=1,
    comment_parent_id=0,
    comment_time=1653986365,
    user_id=1,
    comment_edit_user_id=1,
    comment_flag_staff=False,
    comment_flag_official=False,
    content="",
):
    return Comment.objects.create(
        comment_id=comment_id,
        comment_parent_id=comment_parent_id,
        comment_time=timestamp_to_datetime(comment_time),
        user_id=user_id,
        comment_edit_user_id=comment_edit_user_id,
        comment_flag_staff=comment_flag_staff,
        comment_flag_official=comment_flag_official,
        content=content,
        match=match,
    )


def create_temporary_match_data(
    match_id=1,
    match_day=1,
    team=None,
    enemy_team=None,
    closed=False,
    team_made_latest_suggestion=None,
    latest_suggestions=None,
    begin=None,
    latest_confirmation_log=None,
    enemy_lineup=None,
    match_begin_confirmed=False,
    comments=None,
):
    if comments is None:
        comments = []
    if latest_suggestions is None:
        latest_suggestions = []
    data = {
        "match_id": match_id,
        "match_day": match_day,
        "team": team if team else team,
        "enemy_team_id": enemy_team.id if enemy_team else None,
        "enemy_lineup": enemy_lineup,
        "closed": closed,
        "team_made_latest_suggestion": team_made_latest_suggestion,
        "latest_suggestions": latest_suggestions,
        "begin": begin,
        "latest_confirmation_log": latest_confirmation_log,
        "result": None,
        "match_begin_confirmed": match_begin_confirmed,
        "comments": comments,
    }
    return TemporaryMatchData(**data)


class SplitBuilder:
    """
    Default:

    * Registration starts 14 days before group stage start: 11.01.2024
    * Registration ends 1 day before group stage start: 24.01.2024
    * Calibration stage starts 4 days before the registration ends: 20.01.2024
    * Calibration stage on the same day as the registration ends: 24.01.2024
    * Group stage starts on 25.01.2024
    * Group stage monday is 29.01.2024
        * 1. match day is 04.02.2024
        * 2. match day is 11.02.2024
        * 3. match day is 18.02.2024
        * 4. match day is 25.02.2024
        * 5. match day is 03.03.2024
        * 6. match day is 10.03.2024
        * 7. match day is 17.03.2024
        * 8. match day is 24.03.2024
    * Group stage ends 9 weeks after group stage start: 28.03.2024
    * Playoffs start 1 week after group stage ends: 04.04.2024
    * Playoffs end 2 weeks after playoffs start: 18.04.2024
    """

    def __init__(self, group_stage_start: datetime.date = None):
        if group_stage_start is None:
            group_stage_start = datetime(2024, 1, 25).date()
        if isinstance(group_stage_start, datetime) or isinstance(group_stage_start, datetime_safe):
            group_stage_start = group_stage_start.date()
        self.split_id = None
        self.name = None
        self.group_stage_start = group_stage_start
        self.registration_start = None
        self.registration_end = None
        self.calibration_stage_start = None
        self.calibration_stage_end = None
        self.group_stage_start_monday = None
        self.group_stage_end = None
        self.playoffs_start = None
        self.playoffs_end = None

    def set_name(self, name: str):
        self.name = name
        return self

    def set_calibration_stage_start(self, calibration_stage_start: datetime.date):
        self.calibration_stage_start = calibration_stage_start
        return self

    def set_calibration_stage_end(self, calibration_stage_end: datetime.date):
        self.calibration_stage_end = calibration_stage_end
        return self

    def set_group_stage_start_monday(self, group_stage_start_monday: datetime.date):
        self.group_stage_start_monday = group_stage_start_monday
        return self

    def set_group_stage_end(self, group_stage_end: datetime.date):
        self.group_stage_end = group_stage_end
        return self

    def set_playoffs_start(self, playoffs_start: datetime.date):
        self.playoffs_start = playoffs_start
        return self

    def set_playoffs_end(self, playoffs_end: datetime.date):
        self.playoffs_end = playoffs_end
        return self

    def build(self):
        split_data = Split.calculate(
            registration_start=self.group_stage_start - timedelta(days=14),
            registration_end=self.group_stage_start - timedelta(days=1),
        )
        return Split.objects.create(
            id=self.split_id,
            name=self.name or f"Split {self.group_stage_start.year}",
            registration_start=self.registration_start or split_data['registration_start'],
            registration_end=self.registration_end or split_data['registration_end'],
            calibration_stage_start=self.calibration_stage_start or split_data['calibration_stage_start'],
            calibration_stage_end=self.calibration_stage_end or split_data['calibration_stage_end'],
            group_stage_start=self.group_stage_start,
            group_stage_start_monday=self.group_stage_start_monday or split_data['group_stage_start_monday'],
            group_stage_end=self.group_stage_end or split_data['group_stage_end'],
            playoffs_start=self.playoffs_start or split_data['playoffs_start'],
            playoffs_end=self.playoffs_end or split_data['playoffs_end'],
        )


class TeamBuilder:
    def __init__(self, team_name: str):
        self.team_name = team_name
        self.players = []
        self.language = Team.Languages.GERMAN
        self.telegram_id = None
        self.discord_channel_id = None
        self.split = None

    def add_players_by_names(self, *player_names):
        for player_name in player_names:
            self.players.append(Player(name=player_name))
        return self

    def set_language(self, language: Team.Languages):
        self.language = language
        return self

    def set_telegram(self, telegram_id: int):
        self.telegram_id = telegram_id
        return self

    def set_discord(self, discord_channel_id: int):
        self.discord_channel_id = discord_channel_id
        return self

    def current_split(self):
        self.split = Split.objects.get_current_split()
        return self

    def build(self):
        team = Team.objects.create(
            name=self.team_name,
            telegram_id=self.telegram_id,
            discord_channel_id=self.discord_channel_id,
            language=self.language,
            split=self.split,
        )
        for player in self.players:
            player.team = team

        return team


class MatchBuilder:
    def __init__(self, match_id: int, team_1: Team):
        self.match_id = match_id
        self.team_1 = team_1
        self.match_day = 2
        self.has_side_choice = False
        self.match_type = Match.MATCH_TYPE_LEAGUE
        self.begin = None
        self.team_2 = None
        self.closed = False

    def set_team_2(self, team: Team):
        self.team_2 = team
        return self

    def set_match_day(self, match_day: int):
        self.match_day = match_day
        split = Split.objects.get_current_split()
        if match_day == Match.MATCH_DAY_PLAYOFF:
            self.match_type = Match.MATCH_TYPE_PLAYOFF
            begin = split.group_stage_start_monday + timedelta(days=(7 * 10) - 1)
        elif match_day == Match.MATCH_DAY_TIEBREAKER:
            self.match_type = Match.MATCH_TYPE_LEAGUE
            begin = split.group_stage_start_monday + timedelta(days=(7 * 9) - 1)
        else:
            begin = split.group_stage_start_monday + timedelta(days=(7 * match_day) - 1)
        self.begin = make_aware(datetime.combine(begin, time(20, 0)))
        return self

    def does_have_side_choice(self):
        self.has_side_choice = True
        return self

    def set_match_type(self, match_type: str):
        self.match_type = match_type
        if match_type == Match.MATCH_TYPE_PLAYOFF:
            self.match_day = 0
        return self

    def begin_at(self, begin: datetime):
        self.begin = begin
        return self

    def set_closed(self):
        self.closed = True
        return self

    def build(self):
        Match.objects.create(
            match_id=self.match_id,
            team=self.team_1,
            enemy_team=self.team_2,
            match_day=self.match_day,
            has_side_choice=self.has_side_choice,
            match_type=Match.MATCH_TYPE_LEAGUE,
            begin=self.begin,
            split=Split.objects.get_current_split(),
            closed=self.closed,
        )
