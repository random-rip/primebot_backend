from abc import abstractmethod
from functools import reduce

from modules.providers.prime_league import PrimeLeagueProvider

DEFAULT_PROVIDER = PrimeLeagueProvider


class Maker:
    """
    Every Processor needs to inherit of this MakerClass at first place!
    """

    def __init__(self, provider=None, **kwargs):
        if provider is None:
            self.provider = DEFAULT_PROVIDER()
        else:
            self.provider = provider()
        self.data = self._provider_method(**kwargs)

    @property
    @abstractmethod
    def _provider_method(self):
        pass
