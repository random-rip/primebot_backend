import logging

import django
from django import db

from app_prime_league.models import Team


def mysql_has_gone_away(fn):
    """
    This decorator function checks if my sql has gone away and establish a new connection if so.
    :param fn:
    :return:
    """
    def wrapper(*args, **kwargs):
        try:
            Team.objects.exists()
        except django.db.utils.OperationalError as e:
            log_text = f"{e}: TRY ESTABLISH NEW CONNECTION"
            logging.getLogger("commands_logger").info(log_text)
            db.close_old_connections()
        finally:
            return fn(*args, **kwargs)

    return wrapper
