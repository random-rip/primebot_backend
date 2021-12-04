from abc import abstractmethod

from modules.processors.base_processor import BaseConnector, BaseProcessor


class BaseTeamProcessor(BaseProcessor):

    @abstractmethod
    def get_summoner_names(self):
        pass

    @abstractmethod
    def get_members(self):
        pass

    @abstractmethod
    def get_team_tag(self):
        pass

    @abstractmethod
    def get_matches(self):
        pass

    @abstractmethod
    def get_team_name(self):
        pass

    @abstractmethod
    def get_current_division(self):
        pass

    @abstractmethod
    def get_logo(self):
        pass


class TeamDataProcessor(BaseTeamProcessor, BaseConnector):
    """
    Converting json data to functions and providing these.
    """

    @property
    def _provider_method(self):
        return self.provider.get_team

    def get_summoner_names(self):
        pass

    def get_team_tag(self):
        pass

    def get_members(self):
        pass

    def get_matches(self):
        pass

    def get_team_name(self):
        pass

    def get_current_division(self):
        pass

    def get_logo(self):
        pass

    def __init__(self, team_id: int):
        """
        :raises PrimeLeagueConnectionException, TeamWebsite404Exception
        :param team_id:
        """
        super().__init__(team_id=team_id)
