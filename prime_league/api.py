import os

import requests

BASE_URI = "https://www.primeleague.gg/de/leagues/"
BASE_URI_JSON = "https://www.primeleague.gg/ajax/"

api = {
    "matches": {
        "method": requests.get,
        "path": {
            os.getenv("TEAM_ID"): os.getenv("TEAM_ID"),
            "105959": "prm/1504-summer-split-2020/group/509-gruppenphase/5743-division-4-25",
            "105878": "prm/1504-summer-split-2020/group/509-gruppenphase/5591-division-4-17",
            "93008": "prm/1504-summer-split-2020/group/509-gruppenphase/5576-division-4-12",
            "111914": "prm/1504-summer-split-2020/group/509-gruppenphase/5734-division-4-22",

        }
    },
    "match_details": {
        "method": requests.get,
        "path": "matches/",
    },
    "team": {
        "method": requests.get,
        "path": "teams/",
    },
}

api_json = {
    "match_details": {
        "method": requests.post,
        "path": "leagues_match/",
    }
}


def api_json_handler(which, params=None):
    which = api_json.get(which)
    if which is None:
        raise Exception("Endpoint not found")
    request = which.get("method")
    path = BASE_URI_JSON + which.get("path")
    response = request(path, data=params)
    return response


def api_handler(which, params=None, team_id=None):
    endpoint = api.get(which)
    if endpoint is None:
        raise Exception("Endpoint not found")
    request = endpoint.get("method")
    if which == "matches":
        path = BASE_URI + endpoint["path"][team_id]
    else:
        path = BASE_URI + endpoint.get("path")
    path += "/".join(str(x) for x in [params]) if params is not None else ""
    response = request(path)
    return response


def get_matches(team_id, local=False):
    website = api_handler("matches", team_id=team_id).text if not local else get_local_response("../matches.txt")
    return website


def get_website_of_match(match, local=False):
    web_site = api_handler("match_details", match).text if not local else get_local_response("../file_text.txt")
    return web_site


def get_website_of_team(_id):
    web_site = api_handler("team", _id).text
    return web_site


def get_details_json(match):
    json = api_json_handler("match_details", {"id": match, "action": "init"}).text
    return json


def get_local_response(file_path):
    with open(file_path) as file:
        website = file.read()
    return website
