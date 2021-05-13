from datetime import datetime, time
from typing import Union
import pytz


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


def current_game_day():
    start_date = datetime(2021, 6, 7).astimezone(pytz.timezone("Europe/Berlin"))
    current_date = datetime.now().astimezone(pytz.timezone("Europe/Berlin"))
    game_day = ((current_date - start_date) / 7).days + 1
    return game_day
