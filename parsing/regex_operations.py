import re
from typing import Union

from bs4 import BeautifulSoup

from utils.patterns import TEAM_NAME
from utils.utils import timestamp_to_datetime, string_to_datetime


class BaseHTMLParser:
    """
    BaseParserClass. Provides methods used in TeamHTMLParser and MatchHTMLParser.
    """

    def __init__(self, website):
        self.website = website
        self.logs = None
        self.bs4 = BeautifulSoup(website, 'html.parser')
        self._parse_logs()

    def _parse_logs(self):
        log_table = self.bs4.find_all("div", class_="content-subsection-container")[-1]
        log_trs = log_table.find("tbody").find_all("tr")
        self.logs = []
        for tr in log_trs:
            time = tr.find("span", class_="itime").get('data-time')
            user = tr.find_all("span", class_="table-cell-container")[1].contents[-1]
            action = tr.find_all("span", class_="table-cell-container")[2].contents[-1]
            details = [x.extract() for x in tr.find_all("span", class_="table-cell-container")[-1]]
            log = BaseLog.return_specified_log(
                timestamp=time,
                user=user,
                action=action,
                details=details if len(details) > 0 else None,
            )
            if log is not None:
                self.logs.append(log)

    def get_logs(self):
        return self.logs


class TeamHTMLParser(BaseHTMLParser):
    """
    ParserClass for a team website.
    """

    def get_summoner_names(self):
        # TODO WICHTIG! check auf "richtige" Liste und anschließende Neuauswahl
        team_li = self.bs4.find_all("ul")[4].find_all("li")
        names = [i.span.contents[0] for i in team_li]
        return names

    def get_members(self):
        # TODO
        pass

    def get_matches(self):
        games_table = self.bs4.find_all("ul", class_="league-stage-matches")
        games = games_table[-1].find_all("td", class_="col-2 col-text-center")
        game_ids = [td.a.get("href").split("/matches/")[1].split("-")[0] for td in games]
        return game_ids

    def get_team_name(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_name = page_title_div.h1.contents[0]
        return team_name

    def get_team_tag(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_tag = page_title_div.h1.contents[0].split("(")[1].replace(')', '')
        return team_tag


class MatchHTMLParser(BaseHTMLParser):
    """
    ParserClass for a match website.
    """

    def __init__(self, website, team):
        super().__init__(website)

        team_1_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        team_1_id = team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        self.team_is_team_1 = team_1_id != team.id

    def get_enemy_lineup(self):
        for log in self.logs:
            if isinstance(log, LogLineupSubmit):
                team = "1)" if not self.team_is_team_1 else "2)"
                if log.user.split(" ")[-1] == team:
                    return log.details
        return None

    def get_game_closed(self):
        closed = Union[LogPlayed, LogLineupMissing, LogLineupNotReady, LogDisqualified]
        for log in self.logs:
            if isinstance(log, closed.__args__):  # very hacky way here
                return True
            # if isinstance(log, LogPlayed) or \
            #         isinstance(log, LogLineupMissing) or \
            #         isinstance(log, LogLineupNotReady) or \
            #         isinstance(log, LogDisqualified):
            #     return True
        return False

    def get_latest_suggestion(self):
        for log in self.logs:
            if isinstance(log, LogSuggestion):
                return log
        return None

    def get_suggestion_confirmed(self):
        # Soll hier ein Boolean zurückgegeben werden, oder der Ausgewählte Spieltermin?
        timestamp = None
        for log in reversed(self.logs):
            if isinstance(log, LogSuggestion):
                timestamp = log.details[0]
            if isinstance(log, LogSchedulingConfirmation):
                return log.details
            if isinstance(log, LogSchedulingAutoConfirmation):
                return timestamp

        return False

    def get_enemy_team_name(self):
        results = re.finditer(TEAM_NAME, self.website)
        results = [x for x in results]
        name = [x.group("name") for x in results][0]
        if name is None:
            name = [x.group("name_2") for x in results][0]
        return name

    def get_enemy_team_id(self):
        team_1_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        team_2_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team2")[0]
        team_1_id = team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        team_2_id = team_2_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        return team_2_id if self.team_is_team_1 else team_1_id

    def get_game_day(self):
        match_info_div = self.bs4.find_all("div", class_="content-match-subtitles")[0]
        game_day_div = match_info_div.find_all("div", class_="txt-subtitle")[1]
        game_day = game_day_div.contents[0].split(" ")[1]
        return game_day


class BaseLog:

    def __init__(self, timestamp, user, details):
        self.timestamp = timestamp_to_datetime(timestamp)
        self.user = user
        self.details = details

    def __repr__(self):
        return f"{self.__class__.__name__} von {self.user} um {self.timestamp} === Details: {self.details}"

    @staticmethod
    def return_specified_log(timestamp, user, action, details):
        log = (timestamp, user, details)
        if action == "scheduling_suggest":
            return LogSuggestion(*log)
        elif action == "scheduling_confirm":
            return LogSchedulingConfirmation(*log)
        elif action == "lineup_submit":
            return LogLineupSubmit(*log)
        elif action == "played" or action == "lineup_missing" or action == "lineup_notready":
            return LogPlayed(*log)
        elif action == "scheduling_autoconfirm":
            return LogSchedulingAutoConfirmation(*log)
        return None


class LogSuggestion(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)
        print(len(self.details))
        self.details = [string_to_datetime(x[3:]) for x in self.details]


class LogSchedulingConfirmation(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)
        self.details = string_to_datetime(self.details)


class LogSchedulingAutoConfirmation(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)


class LogPlayed(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)


class LogLineupMissing(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)


class LogLineupNotReady(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)


class LogDisqualified(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)


class LogLineupSubmit(BaseLog):

    def __init__(self, timestamp, user, details):
        super().__init__(timestamp, user, details)
        self.details = [(*x.split(":"),) for x in self.details[0].split(", ")]
