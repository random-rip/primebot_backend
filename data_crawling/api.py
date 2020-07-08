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

    def json_handler(self, endpoint, request=requests.post, post_params=None):
        if endpoint is None:
            raise Exception("Endpoint not found")

        path = f"{self.base_uri_ajax}{endpoint}/"
        response = request(url=path, data=post_params, )
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

        :param local: If local is True, the crawler is using text documents from storage folder.
        """
        self.local = local
        self.api = Api()
        self.save_requests = settings.DEBUG and not local
        if self.save_requests:
            print("Consider using the local file system in development to reduce the number of requests.")

    def get_match_website(self, match_id):
        if self.local:
            return get_local_response(f"match_{match_id}.txt")
        resp = self.api.html_handler(f"matches/{match_id}", )
        if resp.status_code == 404:
            return None
        if self.save_requests:
            save_object_to_file(resp.text, f"match_{match_id}.txt")
        return resp.text

    def get_team_website(self, _id):
        if self.local:
            text = get_local_response(f"team_{_id}.txt")
            return text
        resp = self.api.html_handler(f"teams/{_id}")
        if resp.status_code == 404:
            return None
        if self.save_requests:
            save_object_to_file(resp.text, f"team_{_id}.txt")
        return resp.text

    def get_details_json(self, match):
        if self.local:
            return get_local_response(f"match_details_json_{match}.txt")
        resp = self.api.json_handler(f"leagues_match", post_params={"id": match, "action": "init", "language": "de"})
        if resp.status_code == 404:
            return None
        if self.save_requests:
            save_object_to_file(resp.text, f"match_details_json_{match}.txt")
        return resp.text


crawler = Crawler(local=False)
