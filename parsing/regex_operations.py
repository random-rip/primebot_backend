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

    def get_logs(self):
        self.logs = re.finditer(LOGS, self.website)
        return self.logs

    def get_team_name(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_name = page_title_div.h1.contents[0]
        return team_name

    def get_team_tag(self):
        page_title_div = self.bs4.find_all("div", class_="page-title")[0]
        team_tag = page_title_div.h1.contents[0].split("(")[1].replace(')', '')
        return team_tag


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
        # games = [table.find_all("td", class_="col-2 col-text-center") for table in games_table] --> evtl dann mit Kalibrierung
        game_ids = [td.a.get("href").split("/matches/")[1].split("-")[0] for td in games]
        # game_ids = list(dict.fromkeys([x[1] for x in re.findall(MATCH_IDS, website)]))
        return game_ids


class MatchHTMLParser(BaseHTMLParser):
    """
    ParserClass for a match website.
    """

    def get_enemy_lineup(self):
        # TODO
        return []

    def get_game_closed(self):
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

    def get_enemy_team_id(self, own_team_id):
        team_1_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        team_2_div = self.bs4.find_all("div", class_="content-match-head-team content-match-head-team2")[0]
        team_1_id = team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        team_2_id = team_2_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        if team_1_id != own_team_id:
            return team_1_id
        elif team_2_id != own_team_id:
            return team_2_id
        else:
            return -1

    def get_game_day(self):
        match_info_div = self.bs4.find_all("div", class_="content-match-subtitles")[0]
        game_day_div = match_info_div.find_all("div", class_="txt-subtitle")[1]
        game_day = game_day_div.contents[0].split(" ")[1]
        return game_day
