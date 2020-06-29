from app_prime_league.models import Player
from utils.utils import timestamp_to_datetime, string_to_datetime


class BaseLog:

    def __init__(self, obj):
        if not isinstance(obj, dict):
            self.created_at = timestamp_to_datetime(obj.group("created_at"))
            self.name = obj.group("name")
            self.team = obj.group("team")
            self.action = obj.group("action")
            self.details = obj.group("details")
        else:
            self.created_at = timestamp_to_datetime(obj["created_at"])
            self.name = obj["name"]
            self.team = obj["team"]
            self.action = obj["action"]
            self.details = obj["details"]

    def __repr__(self):
        return "Von {} um {}:\n=== Aktion: {} => Details: {}\n".format(self.name, self.created_at, self.action,
                                                                       self.details)


class LogSuggestion(BaseLog):

    def __init__(self, obj):
        super().__init__(obj)
        if not isinstance(obj, dict):
            self.details = [string_to_datetime(x[3:]) for x in self.details.split("<br>")]
        else:
            self.details = [string_to_datetime(x) for x in self.details]


class LogSchedulingConfirmation(BaseLog):

    def __init__(self, obj):
        super().__init__(obj)
        self.details = string_to_datetime(self.details)


class LogSchedulingAutoConfirmation(BaseLog):

    def __init__(self, obj):
        super().__init__(obj)
        self.details = None


class LogGamesPlayed(BaseLog):

    def __init__(self, obj):
        super().__init__(obj)


class LogLineupSubmit(BaseLog):

    def __init__(self, obj):
        super().__init__(obj)
        if not isinstance(obj, dict):
            self.details = [(x.split(":")) for x in self.details.split(", ")]
            self.details = [Player(x[0], x[1]) for x in self.details]
        else:
            self.details = [Player(x["id"], x["name"]) for x in self.details]