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


class RandomAnimal:
    animals = [CatAPI, DogAPI]

    @staticmethod
    def get_url():
        Klass = random.choice(RandomAnimal.animals)
        try:
            return Klass.get_url()
        except Exception:
            raise ConnectionError("Not accessible")
