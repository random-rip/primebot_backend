from django.conf import settings

from .prime_league import PrimeLeagueProvider
from .request_queue_provider import RequestQueueProvider


def get_provider(**provider_kwargs):
    """Let the environment decide which provider to use."""
    if settings.FILES_FROM_STORAGE:
        return PrimeLeagueProvider()
    return RequestQueueProvider(**provider_kwargs)
