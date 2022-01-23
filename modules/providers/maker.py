from abc import abstractmethod

from deprecated import deprecated

from modules.providers.prime_league import PrimeLeagueProvider

DEFAULT_PROVIDER = PrimeLeagueProvider


@deprecated(version="2.0", reason="Führt zu Overhead, und kann nicht gut getestet werden")
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
