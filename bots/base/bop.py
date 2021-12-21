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
        url = 'https://cataas.com/cat/gif'
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
        Klass = random.choice(GIFinator.apis)
        try:
            return Klass.get_url()
        except Exception:
            # Wir können auf die statische DogAPI zurückgreifen anstatt einen Error zu schmeissen. Und nur wenn die auch
            # fehlschlägt einen Error schmeissen, der abgefangen wird. Dann wird ein Text zum Team zurückgegeben.
            raise ConnectionError("Not accessible")
