import os
import re
import requests
from bs4 import BeautifulSoup
from patterns import LOGS, SUMMONER_NAMES, ENEMY_TEAM_ID, GAME_DAY, TEAM_NAME, MATCH_IDS

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

TEAMS_URL = "https://www.primeleague.gg/de/leagues/teams/"
MATCHES_URL = "https://www.primeleague.gg/de/leagues/matches/"


class RegexOperator:

    def __init__(self):
        pass

    @staticmethod
    def get_logs(website):
        # soup = BeautifulSoup(website, 'html.parser')
        logs = re.finditer(LOGS, website)

        return logs

    @staticmethod
    def get_summoner_names(website):
        team_url = BeautifulSoup(website, 'html.parser')
        # print(team_url.find_all("ul")[4])
        # TODO WICHTIG! check auf "richtige" Liste und anschließende Neuauswahl
        team_li = team_url.find_all("ul")[4].find_all("li");
        names = [i.span.contents[0] for i in team_li]
        return names

    @staticmethod
    def get_enemy_team_id(website):
        match_url = BeautifulSoup(website, 'html.parser')
        team_1_div = match_url.find_all("div", class_="content-match-head-team content-match-head-team1")[0]
        team_2_div = match_url.find_all("div", class_="content-match-head-team content-match-head-team2")[0]
        team_1_id = team_1_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        team_2_id = team_2_div.contents[1].contents[1].get("href").split("/teams/")[1].split("-")[0]
        if team_1_id != os.getenv("TEAM_ID"):
            return team_1_id
        elif team_2_id != os.getenv("TEAM_ID"):
            return team_2_id
        else:
            return -1

    @staticmethod
    def get_game_day(website): #of match
        match_url = BeautifulSoup(website, 'html.parser')
        match_info_div = match_url.find_all("div", class_="content-match-subtitles")[0]
        game_day_div = match_info_div.find_all("div", class_="txt-subtitle")[1]
        game_day = game_day_div.contents[0].split(" ")[1]
        return game_day

    @staticmethod
    def get_enemy_team_name(website):
        results = re.finditer(TEAM_NAME, website)
        results = [x for x in results]
        name = [x.group("name") for x in results][0]
        if name is None:
            name = [x.group("name_2") for x in results][0]
        return name

    @staticmethod
    def get_matches(website):
        game_ids = list(dict.fromkeys([x[1] for x in re.findall(MATCH_IDS, website)]))
        return game_ids
