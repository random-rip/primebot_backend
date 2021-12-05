from abc import abstractmethod

from modules.parsing.logs import BaseLog, LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime
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
        super().__init__(match_id=match_id)
        self.team_id = team_id
        self.team_is_team_1 = self.data_match.get("team_id_id") == team_id
        self.logs = []
        self.__parse_logs()

    def __parse_logs(self):
        logs = self.data.get("logs", [])
        for i in reversed(logs):
            log = BaseLog.return_specified_log(
                timestamp=i.get("log_time"),
                user_id=i.get("user"),
                action=i.get("log_action"),
                details=i.get("log_details"),
            )
            if log is not None:
                self.logs.append(log)

    @property
    def _provider_method(self):
        return self.provider.get_match

    @property
    def data_match(self):
        return self.data.get("match", {})

    @property
    def data_stage(self):
        return self.data.get("stage", {})

    @property
    def data_group(self):
        return self.data.get("group", {})

    def get_enemy_lineup(self):
        lineup = self.data.get("line_ups", [])
        return [x["user_id"] for x in lineup if x["team_id"] != self.team_id]

    def get_game_closed(self):
        """
        possible match_status: ["upcoming", "pending", "finished"]
        """
        return self.data_match.get("match_status", None) == "finished"

    def get_game_result(self):
        """
        If game_result is set, the first number indicates the score that the team reached.
        """
        match_score_1 = self.data_match.get('match_score_1', None)
        match_score_2 = self.data_match.get('match_score_2', None)
        return f"{match_score_1}:{match_score_2}" if self.team_is_team_1 else f"{match_score_2}:{match_score_1}"

    def get_latest_suggestion(self):
        """

        :return: Tuple: (Boolean: if requested team made the suggestion or not, suggestion_array)
        """
        status = self.data_match.get("match_scheduling_status")
        if status == 0:
            return
        suggestions = [
            self.data_match.get("match_scheduling_suggest_0"),
            self.data_match.get("match_scheduling_suggest_1"),
            self.data_match.get("match_scheduling_suggest_2"),
        ]
        status = True if status == 1 else False
        # TODO parse
        return status == self.team_is_team_1, [x for x in suggestions if x]

    def get_game_begin(self):
        """
        :return: default game_begin or set game_begin
        """
        # TODO parse
        return self.data_match.get("match_time")

    def get_enemy_team_id(self):
        return self.data_match.get("team_id_2") if self.team_is_team_1 else self.data_match.get("team_id_1")

    def get_game_day(self):
        return self.data_match.get("match_playday")

    def get_comments(self):
        self.data.get("comments")

    def get_match_time_set(self):
        """
        :return: Tuple(game_begin, latest confirmation_log or change_time_log)
        """
        specified_log = None
        for log in self.logs:
            if isinstance(log, (LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogChangeTime)):
                specified_log = log
                break
        if specified_log is None:
            return None, None
        return self.get_game_begin(), specified_log
