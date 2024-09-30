from abc import ABC, abstractmethod


class Provider(ABC):
    @abstractmethod
    def get_team(self, team_id: int):
        pass

    @abstractmethod
    def get_match(self, match_id: int):
        pass
