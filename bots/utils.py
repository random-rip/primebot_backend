import logging

import django
from discord.utils import escape_markdown as escape_discord_markdown
from django import db
from django.utils.translation import ngettext
from telegram.utils.helpers import escape_markdown as escape_telegram_markdown

from app_prime_league.models import Team


def mysql_has_gone_away_decorator(fn):
    """
    This decorator function checks if my sql has gone away and establish a new connection if so.
    :param fn:
    :return:
    """

    def wrapper(*args, **kwargs):
        mysql_has_gone_away()
        return fn(*args, **kwargs)

    return wrapper


def mysql_has_gone_away(*args):
    try:
        Team.objects.exists()
    except django.db.utils.OperationalError as e:
        log_text = f"{e}: TRY ESTABLISH NEW CONNECTION"
        logging.getLogger("django").info(log_text)
        db.close_old_connections()
    finally:
        return True


def format_time_left(hh, mm):
    hours = ngettext("%d hr", "%d hrs", hh) % hh
    minutes = ngettext("%d min", "%d min", mm) % mm
    return f"{hours} {minutes}"


def esc_md_t(text: str):
    """Escape MarkdownV2 for Telegram"""
    return escape_telegram_markdown(text=text, version=2)


def esc_md_d(text: str):
    """Escape Markdown for Discord"""
    return escape_discord_markdown(text=text)
