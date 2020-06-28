import re

from patterns import LOGS, SUMMONER_NAMES, ENEMY_TEAM_ID, GAME_DAY, TEAM_NAME, MATCH_IDS


class RegexOperator:

    def __init__(self):
        pass

    @staticmethod
    def get_logs(website):
        logs = re.finditer(LOGS, website)
        return logs

    @staticmethod
    def get_summoner_names(website):
        names = re.finditer(SUMMONER_NAMES, website)
        names = [x.group("name").replace(" ", "") for x in names]
        return names

    @staticmethod
    def get_enemy_team_id(website):
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
