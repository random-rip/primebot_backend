import random
from abc import abstractmethod

import requests

from bots.telegram_interface.tg_singleton import send_message_to_devs


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
        animal = random.choice(GIFinator.apis)
        try:
            return animal.get_url()
        except Exception as e:
            send_message_to_devs(f"bop raised an exception: {e}")
            raise ConnectionError("Not accessible")
