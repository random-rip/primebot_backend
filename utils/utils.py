import hashlib
import re
from datetime import datetime, time
from typing import Union

import pytz
from babel import dates as babel
from django.conf import settings
from django.utils import translation, timezone

from utils.exceptions import CouldNotParseURLException, Div1orDiv2TeamException


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
    current_date = timezone.now().astimezone(pytz.timezone("Europe/Berlin"))
    return count_weeks(settings.CURRENT_SPLIT_START, current_date)


def count_weeks(split_start: datetime, another: datetime):
    match_day = ((another - split_start) / 7).days + 1
    return match_day


def get_valid_team_id(value: Union[str, int]) -> int:
    """
    Try to convert value to integer. If it fails, check if "/leagues/" is in value (div 1 and div 2 teams
    cannot be registered, raises Div1orDiv2TeamException). After that try to parse the team ID from the given string.
    Args:
        value: URL string or TeamID

    Returns: int: Team ID
    Raises: CouldNotParseURLException, Div1orDiv2TeamException
    """
    if is_url(value=value):
        if "/leagues/" not in value:
            raise Div1orDiv2TeamException()
        try:
            return int(value.split("/teams/")[-1].split("-")[0])
        except Exception:
            raise CouldNotParseURLException()
    try:
        return int(value)
    except ValueError:
        raise CouldNotParseURLException()


def is_url(value):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, value) is not None


class Encoder:
    __hash_func = hashlib.sha256
    _encoding = "utf-8"
    digest_size = 10

    @classmethod
    def hash(cls, value) -> str:
        if not isinstance(value, str):
            value = str(value)
        value = value.encode(cls._encoding)
        return cls.__hash_func(value).hexdigest()

    @classmethod
    def blake2b(cls, value, ) -> str:
        if not isinstance(value, str):
            value = str(value)
        value = value.encode(cls._encoding)
        return hashlib.blake2b(value, digest_size=cls.digest_size).hexdigest()


def format_datetime(x: datetime):
    clock_label = "'Uhr'" if translation.get_language() == "de" else "a"
    return babel.format_datetime(x, format=f"EEEE, d. MMMM y H:mm {clock_label}", locale=translation.get_language(),
                                 tzinfo=babel.get_timezone(settings.TIME_ZONE))
