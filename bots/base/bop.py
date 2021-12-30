import random
from abc import abstractmethod

import requests


class AnimalAPI:
    @classmethod
    @abstractmethod
    def get_url(cls):
        return


class CatAPI(AnimalAPI):
    @classmethod
    def get_url(cls):
        contents = requests.get('https://cataas.com/c/gif?json=true').json()
        url = 'https://cataas.com'+contents['url']
        return url


class DogAPI(AnimalAPI):
    @classmethod
    def get_url(cls):
        contents = requests.get('https://api.thedogapi.com/v1/images/search?mime_types=gif').json()
        url = contents[0]['url']
        return url


class GIFinator:
    apis = [CatAPI, DogAPI]

    @staticmethod
    def get_gif(team=None):
        # Todo implement personalisiertes GIF über team
        animal = random.choice(GIFinator.apis)
        try:
            return animal.get_url()
        except Exception:
            raise ConnectionError("Not accessible")
