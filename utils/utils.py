from datetime import datetime, time
from typing import Union

import pytz

from utils.exceptions import CouldNotParseURLException


def serializer(obj: Union[datetime, time]):
    if isinstance(obj, datetime):
        serial = obj.replace().timestamp()
        return serial

    if isinstance(obj, time):
        serial = obj.timestamp()
        return serial

    return obj.__dict__


def string_to_datetime(x, timestamp_format='%a, %d %b %Y %H:%M:%S %z'):
    return datetime.strptime(x, timestamp_format).astimezone(pytz.utc) \
        if isinstance(x, str) else timestamp_to_datetime(x)


def timestamp_to_datetime(x):
    if not isinstance(x, int):
        x = int(x)
    return datetime.fromtimestamp(x).astimezone(pytz.utc)


def current_match_day():
    start_date = datetime(2022, 2, 7).astimezone(pytz.timezone("Europe/Berlin"))
    current_date = datetime.now().astimezone(pytz.timezone("Europe/Berlin"))
    match_day = ((current_date - start_date) / 7).days + 1
    return match_day


def get_valid_team_id(response):
    try:
        team_id = int(response)
    except Exception:
        try:
            team_id = int(response.split("/teams/")[-1].split("-")[0])
        except Exception:
            raise CouldNotParseURLException()
    return team_id
