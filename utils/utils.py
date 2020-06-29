from datetime import datetime, time
from typing import Union


def serializer(obj: Union[datetime, time]):
    if isinstance(obj, datetime):
        serial = obj.replace().timestamp()
        return serial

    if isinstance(obj, time):
        serial = obj.timestamp()
        return serial

    return obj.__dict__


def string_to_datetime(x):
    return datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None) \
        if isinstance(x, str) else timestamp_to_datetime(x)


def timestamp_to_datetime(x):
    if not isinstance(x, int):
        x = int(x)
    return datetime.fromtimestamp(x)
