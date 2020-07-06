import os

import requests

from prime_league_bot import settings


def get_local_response(file_name):
    file_path = os.path.join(settings.STORAGE_DIR, file_name)
    with open(file_path, 'r', encoding='utf8') as f:
        text = f.read()
    print("Object loaded from: {}".format(file_path))
    return text


def save_object_to_file(obj, file_name):
    file_path = os.path.join(settings.STORAGE_DIR, file_name)
    with open(file_path, 'w', encoding='utf8') as f:
        f.write(obj)
    print("Object saved into: {} ".format(file_path))


class Api:
    def __init__(self):
        self.base_uri = settings.BASE_URI
        self.base_uri_ajax = settings.BASE_URI_AJAX

    def json_handler(self, endpoint, request=requests.get, post_params=None):
        if endpoint is None:
            raise Exception("Endpoint not found")

        path = f"{self.base_uri}{endpoint}/"
        response = request(path, data=post_params, )
        return response

    def html_handler(self, endpoint, request=requests.get, query_params=None, team_id=None):
        if endpoint is None:
            raise Exception("Endpoint not found")

        path = f"{self.base_uri}{endpoint}"
        path += "/".join(str(x) for x in [query_params]) if query_params is not None else ""
        response = request(path)
        return response


class Crawler:

    def __init__(self, local: bool = False):
        """

        :param local Boolean: If local is True, the crawler is using text documents from storage folder.
        """
        self.local = local
        self.api = Api()
        self.save_requests = settings.DEBUG and not local
        if self.save_requests:
            print("Consider using the local file system in development to reduce the number of requests.")

    def get_match_website(self, match_id):
        if self.local:
            return get_local_response(f"match_{match_id}.txt")
        text = self.api.html_handler(f"matches/{match_id}", ).text
        if self.save_requests:
            save_object_to_file(text, f"match_{match_id}.txt")
        return text

    def get_team_website(self, _id):
        if self.local:
            text = get_local_response(f"team_{_id}.txt")
            return text
        text = self.api.html_handler(f"teams/{_id}").text
        if self.save_requests:
            save_object_to_file(text, f"team_{_id}.txt")
        return text

    def get_details_json(self, match):
        if self.local:
            return get_local_response(f"match_details_json_{match}.txt")
        text = self.api.json_handler("leagues_match/", post_params={"id": match, "action": "init"}).text
        if self.save_requests:
            save_object_to_file(text, f"match_details_json_{match}.txt")
        return text


crawler = Crawler(local=False)
