import logging

import django
from django import db

from app_prime_league.models import Team


def mysql_has_gone_away_decorator(fn):
    """
    This decorator function checks if my sql has gone away and establish a new connection if so.
    :param fn:
    :return:
    """
    def wrapper(*args, **kwargs):
        print("YUhu wir sind hieR")
        mysql_has_gone_away()
        return fn(*args, **kwargs)
    return wrapper


def mysql_has_gone_away(*args):
    try:
        Team.objects.exists()
    except django.db.utils.OperationalError as e:
        log_text = f"{e}: TRY ESTABLISH NEW CONNECTION"
        logging.getLogger("commands_logger").info(log_text)
        db.close_old_connections()
