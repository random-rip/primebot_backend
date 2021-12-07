import json

from bs4 import BeautifulSoup

from modules.parsing.logs import LogSchedulingConfirmation, LogSchedulingAutoConfirmation, LogSuggestion, LogChangeTime, \
    BaseMatchIsOverLog, LogChangeStatus, LogScoreReport, BaseLog
from utils.utils import timestamp_to_datetime, string_to_datetime


class BaseHTMLParser:
    """
    BaseParserClass. Provides methods used in TeamHTMLParser and MatchHTMLParser.
    """

    def __init__(self, website):
        self.bs4 = BeautifulSoup(website, 'html.parser')
        self.logs = None
        self._parse_logs()

    def _parse_logs(self):
        pass

    def get_logs(self):
        return self.logs


class TeamHTMLParser(BaseHTMLParser):
    """
    ParserClass for a team website.
    """

    def get_members(self):
        team_li = self.bs4.find_all("ul", class_="content-portrait-grid-l")[0].find_all("li")
        leader_choices = ["Leader", "Captain"]
        members = []
        for i in team_li:
            try:
                user_id = i.a.get("href").split("/users/")[-1].split("-")[0]
                h3_content = i.h3.contents[0]
                span_content = i.span.contents[0]
                is_leader = i.find("div", class_="txt-subtitle").contents[0] in leader_choices
                members.append((user_id, h3_content, span_content, is_leader))
            except IndexError:
                continue
        return members

    def get_matches(self):
        games_table = self.bs4.find_all("ul", class_="league-stage-matches")
        try:
            games = games_table[-1].find_all("td", class_="col-2 col-text-center")
            game_ids = [td.a.get("href").split("/matches/")[1].split("-")[0] for td in games]
            return game_ids
        except IndexError:
            return []

    def get_team_name(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_name = page_title_div.h1.contents[0].split(" (")[0]
        return team_name

    def get_team_tag(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_tag = page_title_div.h1.contents[0].split("(")[1].replace(')', '')
        return team_tag

    def get_current_division(self):
        logo_box = self.bs4.find("div", class_="content-portrait-head")
        div_li = logo_box.find("li", class_="wide")
        try:
            division = div_li.a.contents[0].split("Division ")[-1]
        except AttributeError:
            return None
        return division

    def get_logo(self):
        logo_box = self.bs4.find("div", class_="content-portrait-head")
        logo_div = logo_box.find("div", class_="image-present")
        logo = logo_div.img
        logo_url = logo.get("src")
        return logo_url


class MatchHTMLParser(BaseHTMLParser):
    """
    ParserClass for a match website.
    """

    def __init__(self, website, json_match, json_comments, team, ):
        super().__init__(website)
        self.json_match = json.loads(json_match)
        self.json_comments = json.loads(json_comments)
        team_1_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        # TODO: Die Zeile wirft einen Index Error, wenn bei einem Match nur ein Team vorhanden ist
        team_1_id = int(team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0])
        self.team_is_team_1 = team_1_id == team.id
        self.website = website

    def _parse_logs(self):
        log_table = self.bs4.find_all("div", class_="content-subsection-container")[-1]
        log_trs = log_table.find("tbody").find_all("tr")
        self.logs = []
        for tr in log_trs:
            time = tr.find("span", class_="itime").get('data-time')
            user = tr.find_all("span", class_="table-cell-container")[1].contents[-1]
            action = tr.find_all("span", class_="table-cell-container")[2].contents[-1]
            details = [x for x in tr.find_all("span", class_="table-cell-container")[-1] if isinstance(x, str)]
            log = BaseLog.return_specified_log(
                timestamp=time,
                user_id=user.split(" (Team")[0],
                action=action,
                details=details,
            )
            if log is not None:
                self.logs.append(log)

    def get_enemy_lineup(self):
        lineup = self.json_match["lineups"]["1"] if not self.team_is_team_1 else self.json_match["lineups"]["2"]
        members = [(x["id"], x["name"], x["gameaccounts"][0], None) for x in lineup]
        return None if len(members) == 0 else members

    def get_game_closed(self):
        for log in self.logs:
            if isinstance(log, BaseMatchIsOverLog):
                return True
            if isinstance(log, LogChangeStatus) and log.details == "finished":
                return True
        if len([x for x in self.logs if isinstance(x, LogScoreReport)]) == 2:
            return True
        return False

    def get_game_result(self):
        result_div = self.bs4.find("span", class_="league-match-result")
        if result_div is None:
            return None
        result = result_div.contents[0]
        scores = result.split(":")
        return f"{scores[0]}:{scores[1]}" if self.team_is_team_1 else f"{scores[1]}:{scores[0]}"

    def get_latest_suggestion(self):
        for log in self.logs:
            if isinstance(log, LogSuggestion):
                return log
        return None

    def get_game_begin(self) -> tuple:
        """
        Returns match begin timestamp if it is in logs
        :return Tuple: First argument: confirmed timestamp, second argument: log
        """
        for log in self.logs:
            if isinstance(log, LogSchedulingConfirmation):
                return log.details, log
            if isinstance(log, LogSchedulingAutoConfirmation):
                timestamp = None
                for sug_log in reversed(self.logs):
                    if isinstance(sug_log, LogSuggestion):
                        timestamp = sug_log.details[0]
                return timestamp, log
            if isinstance(log, LogChangeTime):
                return log.details, log
        return None, False

    def get_enemy_team_id(self):
        team_1_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        team_2_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team2")[0]
        team_1_id = team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        team_2_id = team_2_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        return team_2_id if self.team_is_team_1 else team_1_id

    def get_game_day(self):
        match_info_div = self.bs4.find_all("div", class_="content-match-subtitles")[0]
        try:
            game_day_div = match_info_div.find_all("div", class_="txt-subtitle")[
                1]  # Wirft IndexError bei Playoff-Spielen
            game_day = game_day_div.contents[0].split(" ")[1]  # wirft IndexError bei "Tiebreaker" als game_day
            return int(game_day)
        except IndexError:
            return None

    def get_comments(self):
        comments_from_json = self.json_comments["comments"]
        match_id_from_json = self.json_match["match_id"]

        comments = []
        for x in comments_from_json:
            len_of_comment = len(x["content_orig"])
            comments.append((
                match_id_from_json,
                x["id"],
                x["parent"] if not x["parent"] == 0 else None,
                x["content_orig"][:3000 if len_of_comment >= 3000 else len_of_comment],
                len_of_comment > 3000,
                x["user_name"],
                x["user_id"]
            ))
        # TODO: Childen Parsen @Grayknife
        return None if len(comments) == 0 else comments



