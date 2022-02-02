from abc import abstractmethod

from modules.providers.prime_league import PrimeLeagueProvider


class __TeamDataMethods:

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


class TeamDataProcessor(__TeamDataMethods, ):
    """
    Converting json data to functions and providing these.
    """
    ROLE_PLAYER = 10
    ROLE_CAPTAIN = 20
    ROLE_LEADER = 30

    def __init__(self, team_id: int):
        """
        :raises PrimeLeagueConnectionException, TeamWebsite404Exception
        :param team_id:
        """
        self.data = PrimeLeagueProvider.get_team(team_id=team_id)

    @property
    def data_team(self):
        return self.data.get("team", {})

    def get_team_tag(self):
        return self.data_team.get("team_short")

    def get_members(self):
        def _parse_member(x):
            return x["user_id"], x["user_name"], x["account_value"], x["tu_status"] in [self.ROLE_LEADER,
                                                                                        self.ROLE_CAPTAIN]

        members = [_parse_member(x) for x in self.data.get("members", [])]
        return members

    def get_matches(self):
        return self.data.get("matches", [])

    def get_team_name(self):
        return self.data_team.get("team_name")

    def get_current_division(self):
        # TODO Last Item of "stages", but is currently an empty list
        return "4.4"

    def get_logo(self):
        return self.data_team.get("team_logo_img_url")
