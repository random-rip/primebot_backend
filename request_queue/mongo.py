from dataclasses import dataclass

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


@dataclass
class Conf:
    url: str = None
    serverSelectionTimeoutMS: int = 5_000
    db_name: str = "request_queue"
    collection = "request_queue"

    def __post_init__(self):
        if self.url is None:
            self.url = settings.MONGODB_URI

    @property
    def connection_attrs(self) -> dict:
        return {"host": self.url, "serverSelectionTimeoutMS": self.serverSelectionTimeoutMS}


class MongoConnector:
    _instance = None

    def __init__(self, config: Conf = None):
        self._conf = config or Conf()
        self._client = self.get_connection()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> MongoClient:
        try:
            client = MongoClient(**self._conf.connection_attrs)
            client.server_info()
            return client
        except ServerSelectionTimeoutError:
            raise Exception("Could not connect to MongoDB server.")

    @property
    def client(self) -> MongoClient:
        return self._client

    @property
    def db(self):
        return self._client[self._conf.db_name]

    def close(self):
        """Close the in memory queue connection."""
        self._client.close()
