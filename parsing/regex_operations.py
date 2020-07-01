import re

from utils.patterns import LOGS, SUMMONER_NAMES, ENEMY_TEAM_ID, GAME_DAY, TEAM_NAME, MATCH_IDS


class HTMLParser:

    def __init__(self, website):
        self.website = website
        self.logs = None

    def get_logs(self):
        self.logs = re.finditer(LOGS, self.website)
        return self.logs

    def get_enemy_lineup(self):
        # TODO
        pass

    def get_game_closed(self):
        # TODO
        pass

    def get_latest_suggestion(self):
        # TODO
        pass

    def get_suggestion_confirmed(self):
        # TODO
        pass

    def get_summoner_names(self):
        names = re.finditer(SUMMONER_NAMES, self.website)
        names = [x.group("name").replace(" ", "") for x in names]
        return names

    def get_enemy_team_id(self):
        _id = re.finditer(ENEMY_TEAM_ID, self.website)
        results = [x.group("id") for x in _id]
        return results[0]

    def get_game_day(self):
        day = re.finditer(GAME_DAY, self.website)
        results = [x.group("game_day") for x in day]
        return results[0]

    def get_enemy_team_name(self):
        results = re.finditer(TEAM_NAME, self.website)
        results = [x for x in results]
        name = [x.group("name") for x in results][0]
        if name is None:
            name = [x.group("name_2") for x in results][0]
        return name

    def get_matches(self):
        game_ids = list(dict.fromkeys([x[1] for x in re.findall(MATCH_IDS, self.website)]))
        return game_ids
