from datetime import datetime

import pytz


def string_to_datetime(x, timestamp_format='%Y-%m-%d %H:%M'):
    return datetime.strptime(x, timestamp_format).astimezone(pytz.utc)
