from abc import abstractmethod

from communication_interfaces.message_factory import MessageDispatcher


class Bot:
    def __init__(self, team):
        self.dispatcher = MessageDispatcher(team)

    @abstractmethod
    def register_team(self):
        return

    def _register_team(self, config):
        pass
