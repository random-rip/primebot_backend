from datetime import datetime

import pytz

from app_prime_league.models import Comment
from modules.temporary_match_data import TemporaryComment, TemporaryMatchData
from utils.utils import timestamp_to_datetime


def string_to_datetime(x, timestamp_format='%Y-%m-%d %H:%M'):
    return datetime.strptime(x, timestamp_format).astimezone(pytz.utc)


def create_temporary_comment(comment_id=1, comment_parent_id=0, comment_time=1653986365, user_id=1,
                             comment_edit_user_id=1, comment_flag_staff=False, comment_flag_official=False,
                             content=""):
    return TemporaryComment(
        comment_id=comment_id, comment_parent_id=comment_parent_id, comment_time=comment_time, user_id=user_id,
        comment_edit_user_id=comment_edit_user_id, comment_flag_staff=comment_flag_staff,
        comment_flag_official=comment_flag_official, content=content)


def create_comment(match, comment_id=1, comment_parent_id=0, comment_time=1653986365, user_id=1,
                   comment_edit_user_id=1, comment_flag_staff=False, comment_flag_official=False,
                   content="", ):
    return Comment.objects.create(
        id=comment_id,
        comment_parent_id=comment_parent_id,
        comment_time=timestamp_to_datetime(comment_time),
        user_id=user_id,
        comment_edit_user_id=comment_edit_user_id,
        comment_flag_staff=comment_flag_staff,
        comment_flag_official=comment_flag_official,
        content=content,
        match=match,
    )


def create_temporary_match_data(match_id=1, match_day=1, team=None, enemy_team=None, closed=False,
                                team_made_latest_suggestion=None, latest_suggestions=None, begin=None,
                                latest_confirmation_log=None, enemy_lineup=None, match_begin_confirmed=False,
                                comments=None):
    if comments is None:
        comments = []
    if latest_suggestions is None:
        latest_suggestions = []
    data = {
        "match_id": match_id,
        "match_day": match_day,
        "team": team if team else team,
        "enemy_team_id": enemy_team.id if enemy_team else enemy_team.id,
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
