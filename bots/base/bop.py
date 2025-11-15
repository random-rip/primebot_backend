import random
from abc import abstractmethod

import niquests

from bots.telegram_interface.tg_singleton import send_message_to_devs


class AnimalAPI:
    animal = None
    label = None

    @classmethod
    @abstractmethod
    def get_url(cls) -> str:
        pass


class CatAPI(AnimalAPI):
    animal = 'cat'
    label = "Cats"

    @classmethod
    def get_url(cls):
        return "https://cataas.com/cat/gif"


class DogAPI(AnimalAPI):
    animal = 'dog'
    label = "Dogs"

    @classmethod
    def get_url(cls):
        contents = niquests.get('https://api.thedogapi.com/v1/images/search?mime_types=gif').json()
        url = contents[0]['url']
        return url


class FoxAPI(AnimalAPI):
    animal = 'fox'
    label = "Foxes"

    @classmethod
    def get_url(cls):
        contents = niquests.get('https://randomfox.ca/floof/').json()
        url = contents['image']
        return url


class DuckAPI(AnimalAPI):
    animal = 'duc'
    label = "Ducks"

    @classmethod
    def get_url(cls):
        contents = niquests.get('https://random-d.uk/api/v2/random?type=gif').json()
        url = contents['url']
        return url


class RabbitAPI(AnimalAPI):
    animal = 'rab'
    label = "Rabbits"

    @classmethod
    def get_url(cls):
        contents = niquests.get('https://api.bunnies.io/v2/loop/random/?media=gif').json()
        url = contents['media']['gif']
        return url


class OtterAPI(AnimalAPI):
    animal = 'ott'
    label = "Otters"

    @classmethod
    def get_url(cls):
        return "https://i.imgflip.com/ac80s7.jpg"


class InvalidAnimalException(Exception):
    pass


class Gifinator:
    available_apis: dict[str, AnimalAPI] = {
        api.animal: api for api in [CatAPI, DogAPI, FoxAPI, DuckAPI, RabbitAPI, OtterAPI]
    }
    random_animals: dict[str, AnimalAPI] = {api.animal: api for api in [CatAPI, DogAPI, DuckAPI]}

    @classmethod
    def get_choices(cls) -> list[tuple[str, str]]:
        return [(api.label, api.animal) for api in cls.available_apis.values()]

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
            return random.choice(list(cls.random_animals.values()))
        try:
            return cls.available_apis[animal]
        except KeyError:
            raise InvalidAnimalException
