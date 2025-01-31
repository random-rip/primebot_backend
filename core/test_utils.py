from datetime import datetime
from typing import OrderedDict, Union
from zoneinfo import ZoneInfo

from django.db import models

from core.temporary_match_data import TemporaryComment, TemporaryMatchData


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
    return datetime.strptime(x, timestamp_format).astimezone(ZoneInfo("UTC"))


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
