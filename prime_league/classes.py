import json
from datetime import datetime, time

from api import get_details_json, get_website_of_team
from regex_operations import RegexOperator

TEAM_LEADER = ["Miriiel", "Starscream853", "Isilmacil", "Grayknife", "Kamir", "Itzsofteis", "Pixelqueen"]


class Log:

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


class LogSuggestion(Log):

    def __init__(self, obj):
        super().__init__(obj)
        if not isinstance(obj, dict):
            self.details = [string_to_datetime(x[3:]) for x in self.details.split("<br>")]
        else:
            self.details = [string_to_datetime(x) for x in self.details]


class LogSchedulingConfirmation(Log):

    def __init__(self, obj):
        super().__init__(obj)
        self.details = string_to_datetime(self.details)


class LogSchedulingAutoConfirmation(Log):

    def __init__(self, obj):
        super().__init__(obj)
        self.details = None


class LogGamesPlayed(Log):

    def __init__(self, obj):
        super().__init__(obj)


class LogLineupSubmit(Log):

    def __init__(self, obj):
        super().__init__(obj)
        if not isinstance(obj, dict):
            self.details = [(x.split(":")) for x in self.details.split(", ")]
            self.details = [Player(x[0], x[1]) for x in self.details]
        else:
            self.details = [Player(x["id"], x["name"]) for x in self.details]


class Game:

    def __init__(self, _id, logs, game_day, enemy_team):
        self.game_id = _id
        self.game_day = game_day
        self.enemy_team = enemy_team
        self.logs = [LogManager.get_log_class(obj=x)(x) for x in logs]
        self.suggestion_logs = [x for x in self.logs if isinstance(x, LogSuggestion)]
        if any(isinstance(x, LogSchedulingAutoConfirmation) for x in self.logs):
            self.__scheduling_confirmation_log = [x for x in self.logs if isinstance(x, LogSchedulingAutoConfirmation)]
            self.__scheduling_confirmation_log[0].details = self.suggestion_logs[0].details[0]
        else:
            self.__scheduling_confirmation_log = [x for x in self.logs if isinstance(x, LogSchedulingConfirmation)]
        self.match_ended = len([x for x in self.logs if isinstance(x, LogGamesPlayed)]) > 0

    def __repr__(self):
        return "{}:\n{}".format(self.game_id, self.logs)

    def get_scheduling_confirmation_log(self):
        return self.__scheduling_confirmation_log[0] if len(self.__scheduling_confirmation_log) > 0 else None

    def get_latest_suggestion_log(self, of_enemy=True):
        if len(self.suggestion_logs) == 0:
            return None
        if of_enemy:
            if self.suggestion_logs[0].name not in TEAM_LEADER:
                return self.suggestion_logs[0]
            elif len(self.suggestion_logs) == 2:
                return self.suggestion_logs[1]
        else:
            if self.suggestion_logs[0].name in TEAM_LEADER:
                return self.suggestion_logs[0]
            elif len(self.suggestion_logs) == 2:
                return self.suggestion_logs[2]
        return None

    def create_op_link_of_enemy_lineup(self):
        data = get_details_json(self.game_id)
        data = json.loads(data)
        lineup_1 = data["lineups"]["1"]
        lineup_1 = [x["gameaccounts"][0].replace(" ", "") for x in lineup_1]
        if len(lineup_1) > 0 and len(set(TEAM_LEADER).intersection(lineup_1)) == 0:
            url = "%2C".join(lineup_1)
            return "https://euw.op.gg/multi/query={}".format(url)
        lineup_2 = data["lineups"]["2"]
        lineup_2 = [x["gameaccounts"][0].replace(" ", "") for x in lineup_2]
        if len(lineup_2) > 0 and len(set(TEAM_LEADER).intersection(lineup_2)) == 0:
            url = "%2C".join(lineup_2)
            return "https://euw.op.gg/multi/query={}".format(url)
        return None

    def create_general_op_link_of_enemies(self):
        names = RegexOperator.get_summoner_names((get_website_of_team(self.enemy_team)))
        url = "%2C".join(names)
        return "https://euw.op.gg/multi/query={}".format(url)

    def serialize(self):
        return json.dumps(self, default=serializer)

    @staticmethod
    def deserialize(data):
        _obj = json.loads(data)
        _id = _obj["game_id"]
        game_day = _obj.get("game_day", 0)
        enemy_team = _obj.get("enemy_team", "")
        return Game(_id, _obj["logs"], game_day, enemy_team)


class LogManager:

    @staticmethod
    def get_log_class(obj):
        action = obj.group("action") if not isinstance(obj, dict) else obj["action"]
        if action == "scheduling_suggest":
            return LogSuggestion
        elif action == "scheduling_confirm":
            return LogSchedulingConfirmation
        elif action == "lineup_submit":
            return LogLineupSubmit
        elif action == "played" or action == "lineup_missing" or action == "lineup_notready":
            return LogGamesPlayed
        elif action == "scheduling_autoconfirm":
            return LogSchedulingAutoConfirmation
        return Log


class Player:

    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def __repr__(self):
        return "ID: {} - Name: {}".format(self.id, self.name)


class Comparer:

    def __init__(self, game_old, game_new):
        self.game_old = game_old
        self.game_new = game_new

    def compare_new_suggestion_of_enemy(self):
        if len(self.game_old.suggestion_logs) < len(self.game_new.suggestion_logs) and \
                len(self.game_new.suggestion_logs) > 0 and self.game_new.suggestion_logs[0].name \
                not in TEAM_LEADER:
            return True
        return False

    def compare_new_suggestion_of_our_team(self):
        if len(self.game_old.suggestion_logs) < len(self.game_new.suggestion_logs) and \
                len(self.game_new.suggestion_logs) > 0 and self.game_new.suggestion_logs[0].name \
                in TEAM_LEADER:
            return True
        return False

    def compare_scheduling_confirmation(self):
        old_log = self.game_old.get_scheduling_confirmation_log()
        new_log = self.game_new.get_scheduling_confirmation_log()
        if new_log is not None and old_log is None:
            return True
        return False

    def compare_lineup_confirmation(self):
        link_old = self.game_old.create_op_link_of_enemy_lineup()
        link_new = self.game_new.create_op_link_of_enemy_lineup()
        return True if link_old is None and link_new is not None else False


def serializer(obj):
    if isinstance(obj, datetime):
        serial = obj.replace().timestamp()
        return serial

    if isinstance(obj, time):
        serial = obj.replace().timestamp()
        return serial

    return obj.__dict__


def string_to_datetime(x):
    return datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None) \
        if isinstance(x, str) else timestamp_to_datetime(x)


def timestamp_to_datetime(x):
    if not isinstance(x, int):
        x = int(x)
    return datetime.fromtimestamp(x)
