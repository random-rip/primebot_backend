import json

from app_prime_league.models import Game, Team, Log, Player
from data_crawling.api import Crawler
from parsing.logging import LogSuggestion, LogSchedulingConfirmation, LogLineupSubmit, LogGamesPlayed, \
    LogSchedulingAutoConfirmation, BaseLog
from parsing.regex_operations import HTMLParser
from utils.utils import serializer


class GameManager:

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
        # if len(self.suggestion_logs) == 0:
        #     return None
        # if of_enemy:
        #     if self.suggestion_logs[0].name not in TEAM_LEADER:
        #         return self.suggestion_logs[0]
        #     elif len(self.suggestion_logs) == 2:
        #         return self.suggestion_logs[1]
        # else:
        #     if self.suggestion_logs[0].name in TEAM_LEADER:
        #         return self.suggestion_logs[0]
        #     elif len(self.suggestion_logs) == 2:
        #         return self.suggestion_logs[2]
        return None

    def create_op_link_of_enemy_lineup(self):
        # data = get_details_json(self.game_id)
        # data = json.loads(data)
        # lineup_1 = data["lineups"]["1"]
        # lineup_1 = [x["gameaccounts"][0].replace(" ", "") for x in lineup_1]
        # if len(lineup_1) > 0 and len(set(TEAM_LEADER).intersection(lineup_1)) == 0:
        #     url = "%2C".join(lineup_1)
        #     return "https://euw.op.gg/multi/query={}".format(url)
        # lineup_2 = data["lineups"]["2"]
        # lineup_2 = [x["gameaccounts"][0].replace(" ", "") for x in lineup_2]
        # if len(lineup_2) > 0 and len(set(TEAM_LEADER).intersection(lineup_2)) == 0:
        #     url = "%2C".join(lineup_2)
        #     return "https://euw.op.gg/multi/query={}".format(url)
        return None

    def create_general_op_link_of_enemies(self):
        names = HTMLParser.get_summoner_names(Crawler.get_team_website(self.enemy_team))
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

    @staticmethod
    def create_game_from_website(team: Team, game_id, website, save=False):
        parser = HTMLParser(website)
        game = Game()
        game.game_day = parser.get_game_day()
        game.game_id = game_id
        game.team = team

        enemy_team, _ = Team.objects.get_or_create(id=parser.get_enemy_team_id(), defaults={
            "watch": False
        })
        game.enemy_team = enemy_team

        logs = parser.get_logs()
        logs = [LogManager.get_log_class(obj=x)(x) for x in logs]
        for i in logs:
            log = Log()
            log.timestamp = i.created_at
            log.user, _ = Player.objects.get_or_create(name=i.name)
            log.action = i.action
            log.details = i.details
            log.game = game
            game.log_set.create(
                timestamp=
            )
        if save:
            game.save()
        return game


class PlayerManager:

    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def __repr__(self):
        return "ID: {} - Name: {}".format(self.id, self.name)


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
        return BaseLog
