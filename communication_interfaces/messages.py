from abc import abstractmethod


class BaseMessage:
    def __init__(self, team):
        self.team = team
        self.message = None

    @abstractmethod
    def _generate_message(self):
        pass


class WeeklyNotificationMessage(BaseMessage):
    msg_type = "weekly_notification"

    def __init__(self, team, ):
        super().__init__(team)
        self._generate_message()

    def _generate_message(self):
        self.message = f"some nice msg für das nice Team {self.team.name}"
