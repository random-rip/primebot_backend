LOGS = r"(?:<td><span class=\"table-cell-container\">[\S\s]*?data-time=\")(?P<created_at>\d*)(?:[\S\s]*?<td><span class=\"table-cell-container\">)(?:<i>)?(?P<name>.*?)(?:</i>)?\s\((?:Team (?P<team>(?:[\d]*))|(?P<admin>admin))\)(?:[\S\s]*?<td><span class=\"table-cell-container\">)(?P<action>[\w]*)(?:[\S\s]*?<td><span class=\"table-cell-container\">)(?P<details>.*)(?=</span></td>)"
MATCH_IDS = r"((?:\/matches\/)(?P<match_id>[\d]*)(?:[\w\d\-]*leipzig\d*))(?!.*\1)"
SUMMONER_NAMES = r"(?:LoL Summoner Name \(EU West\)\">)(?P<name>.*)(?=</span>)"
ENEMY_TEAM_ID = r"(?:teams/)(?P<id>\d*)-(?!leipzig)"
GAME_DAY = r"(?:Spieltag )(?P<game_day>\d*)"
TEAM_NAME = r"(?:<h1>.*?: (?P<name>.*?)(?= vs. (?:Leipzig|LES)))|(?:(?:<h1>.*?vs. )(?P<name_2>.*)(?=</h1>))"

# https://www.primeleague.gg/de/leagues/prm/1457-spring-split-2020/
