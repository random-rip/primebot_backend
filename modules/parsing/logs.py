from utils.utils import timestamp_to_datetime, string_to_datetime


class BaseLog:

    def __init__(self, timestamp, user_id, details):
        self.timestamp = timestamp_to_datetime(timestamp)
        self.user_id = user_id
        self.details = details

    def __repr__(self):
        return f"{self.__class__.__name__} von {self.user_id} um {self.timestamp} === Details: {self.details}"

    @staticmethod
    def return_specified_log(timestamp, user_id, action, details):
        log_dict = {
            "scheduling_suggest": LogSuggestion,
            "scheduling_confirm": LogSchedulingConfirmation,
            "lineup_submit": LogLineupSubmit,
            "played": LogPlayed,
            "scheduling_autoconfirm": LogSchedulingAutoConfirmation,
            "disqualify": LogDisqualified,
            "lineup_missing": LogLineupMissing,
            "lineup_notready": LogLineupNotReady,
            "change_time": LogChangeTime,
            "change_status": LogChangeStatus,
            "change_score": LogChangeScore,
            "score_report": LogScoreReport,
            "lineup_fail": LogLineupFail,
            "change_score_status": LogChangeScoreStatus,
        }
        Log = log_dict.get(action, None)
        return None if not Log else Log(timestamp, user_id, details)


class BaseMatchIsOverLog(BaseLog):
    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogSuggestion(BaseLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        self.details = [string_to_datetime(x[3:]) for x in self.details.split("<br>")]


class LogSchedulingConfirmation(BaseLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        self.details = string_to_datetime(self.details)


class LogSchedulingAutoConfirmation(BaseLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogPlayed(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogLineupMissing(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogLineupNotReady(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogDisqualified(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogLineupFail(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogChangeScoreStatus(BaseMatchIsOverLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        prefix = "Manually adjusted score to "
        self.details = self.details[len(prefix):len(prefix) + 3]


class LogChangeStatus(BaseLog):
    """
    self.details can currently be "finished" (Stand 21.03.2021)
    """

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        prefix = "Manually adjusted status to "
        self.details = self.details[len(prefix):]


class LogChangeScore(BaseLog):
    """
    Currently deprecated
    """

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        prefix = "Manually adjusted score to "
        self.details = self.details[len(prefix):]


class LogScoreReport(BaseLog):
    """
    Currently deprecated
    """

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)


class LogLineupSubmit(BaseLog):

    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        self.details = [(*x.split(":"),) for x in self.details.split(", ")]
        self.details = [(int(id_), name) for id_, name in self.details]


class LogChangeTime(BaseLog):
    def __init__(self, timestamp, user_id, details):
        super().__init__(timestamp, user_id, details)
        prefix = "Manually adjusted time to "
        self.details = string_to_datetime(self.details[len(prefix):], timestamp_format="%Y-%m-%d %H:%M %z")