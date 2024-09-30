from dataclasses import dataclass

from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


@dataclass
class Conf:
    url: str
    serverSelectionTimeoutMS: int = 5_000
    db_name: str = "request_queue"
    collection = "request_queue"

    @property
    def connection_attrs(self) -> dict:
        return {"host": self.url, "serverSelectionTimeoutMS": self.serverSelectionTimeoutMS}


class MongoConnector:
    def __init__(self, config: Conf):
        self._conf = config
        self._client = self.get_connection()

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


mongo_connector = MongoConnector(Conf(url=settings.MONGODB_URI))
