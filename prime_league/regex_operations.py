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
    def get_summoner_names(_id):
        req = requests.get(TEAMS_URL + _id, headers)
        team_url = BeautifulSoup(req.content, 'html.parser')
        # print(team_url.find_all("ul")[4])
        # TODO WICHTIG! check auf "richtige" Liste und anschließende Neuauswahl
        team_li = team_url.find_all("ul")[4].find_all("li");
        names = []
        for li in team_li:
            names.append(li.span.contents[0])
        return names

    @staticmethod
    def get_enemy_team_id(match_id):
        url = MATCHES_URL+match_id
        req = requests.get(MATCHES_URL + match_id, headers)
        match_url = BeautifulSoup(req.content, 'html.parser')
        divs = match_url.find_all("div")
        for div in divs:
            if div["class"]==["test"]:
    

        _id = re.finditer(ENEMY_TEAM_ID, website)
        results = [x.group("id") for x in _id]
        return results[0]

    @staticmethod
    def get_game_day(website):
        day = re.finditer(GAME_DAY, website)
        results = [x.group("game_day") for x in day]
        return results[0]

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
