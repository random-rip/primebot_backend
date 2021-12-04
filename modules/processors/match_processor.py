from abc import abstractmethod

from modules.providers.maker import Maker


class _MatchDataFunctions:

    @abstractmethod
    def get_enemy_lineup(self):
        pass

    @abstractmethod
    def get_game_closed(self):
        pass

    @abstractmethod
    def get_game_result(self):
        pass

    @abstractmethod
    def get_latest_suggestion(self):
        pass

    @abstractmethod
    def get_game_begin(self):
        pass

    @abstractmethod
    def get_enemy_team_id(self):
        pass

    @abstractmethod
    def get_game_day(self):
        pass

    @abstractmethod
    def get_comments(self):
        pass


class MatchDataProcessor(Maker, _MatchDataFunctions, ):
    """
    Converting json data to functions and providing these.
    """

    def __init__(self, match_id: int, team_id: int):
        """
        :raises PrimeLeagueConnectionException, TeamWebsite404Exception
        :param match_id:
        :param team_id: team's point of view to the match. For example to determine enemy_team of the match.
        """
        super().__init__(match_id=match_id, team_id=team_id)
        self.team_id = team_id

    def _provider_method(self):
        return self.provider.get_match

    def get_enemy_lineup(self):
        pass

    def get_game_closed(self):
        pass

    def get_game_result(self):
        pass

    def get_latest_suggestion(self):
        pass

    def get_game_begin(self):
        pass

    def get_enemy_team_id(self):
        pass

    def get_game_day(self):
        pass

    def get_comments(self):
        pass
