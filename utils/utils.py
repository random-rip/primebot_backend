import hashlib
from datetime import datetime, time
from typing import Union

import pytz
from babel import dates as babel
from django.conf import settings
from django.utils import translation

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
    start_date = datetime(2022, 6, 6).astimezone(pytz.timezone("Europe/Berlin"))
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
