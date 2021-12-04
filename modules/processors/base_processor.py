from abc import abstractmethod

from modules.provider import PrimeLeagueProvider


class BaseProcessor:
    """
    BaseProviderClass.
    """

    def __init__(self, **kwargs):
        pass


class BaseConnector:
    """
    BaseConnectorClass.
    """

    def __init__(self, connector=PrimeLeagueProvider, **kwargs):
        self.provider = connector()
        self.json = self._provider_method(**kwargs)

    @property
    @abstractmethod
    def _provider_method(self):
        pass
