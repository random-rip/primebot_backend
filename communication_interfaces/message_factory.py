from communication_interfaces.messages import BaseMessage


class MessageDispatcher:

    def __init__(self, team):
        self.team = team
        self._initialize()

    def _initialize(self):
        return

    def dispatch(self, msg):
        assert isinstance(msg, BaseMessage)
        # dispatch the message to all channels of the team
        return
