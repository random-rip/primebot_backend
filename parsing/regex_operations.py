import re

from bs4 import BeautifulSoup

from utils.patterns import LOGS, SUMMONER_NAMES, ENEMY_TEAM_ID, GAME_DAY, TEAM_NAME, MATCH_IDS


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
            content = tr.find_all("span", class_="table-cell-container")[-1].contents
            if len(content) > 0:
                details = content[0]
            else:
                details = None
            self.logs.append({
                "timestamp": time,
                "user": user,
                "action": action,
                "details": details,
            })

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
            if log["action"] == "lineup_submit":

                team = "1)" if not self.team_is_team_1 else "2)"
                if log["user"].split(" ")[-1] == team:
                    return [(*x.split(":"),) for x in log["details"].split(", ")]
        return None

    def get_game_closed(self):
        # action = obj.group("action") if not isinstance(obj, dict) else obj["action"]
        # if action == "scheduling_suggest":
        #     return LogSuggestion
        # elif action == "scheduling_confirm":
        #     return LogSchedulingConfirmation
        # elif action == "lineup_submit":
        #     return LogLineupSubmit
        # elif action == "played" or action == "lineup_missing" or action == "lineup_notready":
        #     return LogGamesPlayed
        # elif action == "scheduling_autoconfirm":
        #     return LogSchedulingAutoConfirmation
        # return Log

        # TODO

        return False

    def get_latest_suggestion(self):
        # TODO
        pass

    def get_suggestion_confirmed(self):
        # TODO
        pass

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
