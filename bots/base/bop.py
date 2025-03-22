import random
from abc import abstractmethod
from typing import Iterable

import niquests

from bots.telegram_interface.tg_singleton import send_message_to_devs


class AnimalAPI:
    animal = None

    @classmethod
    @abstractmethod
    def get_url(cls) -> str:
        pass


class CatAPI(AnimalAPI):
    animal = 'cat'

    @classmethod
    def get_url(cls):
        url = 'https://cataas.com/cat/gif'
        return url


class DogAPI(AnimalAPI):
    animal = 'dog'

    @classmethod
    def get_url(cls):
        contents = niquests.get('https://api.thedogapi.com/v1/images/search?mime_types=gif').json()
        url = contents[0]['url']
        return url


class Gifinator:
    apis: dict[str, AnimalAPI] = {api.animal: api for api in [CatAPI, DogAPI]}

    @classmethod
    def animals(cls) -> Iterable[str]:
        return cls.apis.keys()

    @classmethod
    def get_gif(cls, animal=None) -> str:
        api = cls.get_api(animal)
        try:
            return api.get_url()
        except Exception as e:
            send_message_to_devs("bop raised an exception:", code=str(e))
            raise ConnectionError("Not accessible")

    @classmethod
    def get_api(cls, animal=None):
        if animal is None:
            return random.choice(list(cls.apis.values()))
        try:
            return cls.apis[animal]
        except KeyError:
            raise ValueError("No such animal")
