import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple

from bson import ObjectId
from pymongo import ASCENDING

from core.providers.prime_league import PrimeLeagueProvider
from utils.exceptions import (
    Match404Exception,
    PrimeLeagueConnectionException,
    PrimeLeagueParseException,
    TeamWebsite404Exception,
)

from .mongo import MongoConnector

__all__ = ["EndpointType", "run", "RequestQueue"]

logger = logging.getLogger(__name__)


class EndpointType(Enum):
    MATCH = "match"
    TEAM = "team"


class RequestQueue:
    """
    This class provides an interface for the request queue in MongoDB.
    """

    _instance = None
    REQUEST_COL_NAME = "request_queue"
    RESPONSE_COL_NAME = "responses"

    def __init__(self, connector: MongoConnector = None):
        self.connector = connector or MongoConnector()
        self.queue_collection = self.get_collection(RequestQueue.REQUEST_COL_NAME)
        self.response_collection = self.get_collection(RequestQueue.RESPONSE_COL_NAME)
        self.ensure_indexes()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_collection(self, collection_name):
        return self.connector.db[collection_name]

    def ensure_indexes(self):
        """Ensure indexes for the priority queue."""
        self.queue_collection.create_index([("priority", ASCENDING), ("timestamp", ASCENDING)])
        self.response_collection.create_index([("endpoint", ASCENDING), ("detail_id", ASCENDING)])

    def push(self, endpoint: EndpointType, detail_id, priority: int = 0):
        """Add an item to the queue with a given priority and timestamp."""
        timestamp = datetime.utcnow()
        payload = {"endpoint": endpoint.value, "detail_id": detail_id}
        document = self.queue_collection.insert_one(
            {
                "payload": payload,
                "priority": priority,
                "created_at": timestamp,
                "attempts": 0,
                "last_processed": None,
            }
        )
        print(f"Job with payload {payload} pushed to queue.")
        return str(document.inserted_id)

    def pop(self, retry_interval_seconds: int = 5):
        """Remove and return the item with the highest priority."""
        retry_time = datetime.utcnow() - timedelta(seconds=retry_interval_seconds)
        result = self.queue_collection.find_one_and_delete(
            filter=self._filter(retry_time), sort=[("priority", ASCENDING), ("created_at", ASCENDING)]
        )
        return result

    def _filter(self, retry_time: datetime):
        return {"$or": [{"last_processed": None}, {"last_processed": {"$lt": retry_time}}]}

    def next(self, retry_interval_seconds=5) -> dict | None:
        """Return the item with the highest priority without removing it, considering retry interval."""
        retry_time = datetime.utcnow() - timedelta(seconds=retry_interval_seconds)
        result = self.queue_collection.find_one(
            filter=self._filter(retry_time), sort=[("priority", ASCENDING), ("created_at", ASCENDING)]
        )
        return result

    def delete_entry(self, entry_id: str):
        """Delete an entry from the queue."""
        self.queue_collection.delete_one({"_id": entry_id})

    def get_response(self, endpoint: EndpointType, detail_id: int) -> dict | None:
        return self.response_collection.find_one({"endpoint": endpoint.value, "detail_id": detail_id})

    def job_is_queued(self, job_id: str) -> bool:
        return self.queue_collection.find_one({"_id": ObjectId(job_id)}) is not None


MAXIMUM_SLEEP: int = 1


def __call_api(payload: dict[str, str | int]) -> Tuple[int, dict | None]:
    endpoint = payload["endpoint"]
    detail_id = payload["detail_id"]
    if endpoint == EndpointType.MATCH.value:
        func = PrimeLeagueProvider().get_match
    else:
        func = PrimeLeagueProvider().get_team
    try:
        resp: dict = func(detail_id)
    except PrimeLeagueParseException:
        return 400, None
    except TeamWebsite404Exception:
        return 404, None
    except Match404Exception:
        return 404, None
    except PrimeLeagueConnectionException:
        return 500, None
    else:
        return 200, resp


def __save_to_db(endpoint: str, detail_id: int, data, status_code):
    queue = RequestQueue()
    queue.response_collection.update_one(
        filter={"endpoint": endpoint, "detail_id": detail_id},
        update={
            "$set": {
                "payload": data,
                "status_code": status_code,
                "last_crawled": datetime.utcnow(),
            },
            "$setOnInsert": {
                "endpoint": endpoint,
                "detail_id": detail_id,
            },
        },
        upsert=True,
    )


def __process_job(job):
    print(f"Processing job {job['payload']}...")
    current_attempts = job.get("attempts", 0)
    status_code, data = __call_api(job["payload"])
    endpoint = job["payload"]["endpoint"]
    detail_id = job["payload"]["detail_id"]
    queue = RequestQueue()
    if status_code == 200:
        print(f"Successfully processed job {job['payload']}!")
        __save_to_db(endpoint, detail_id, data, status_code)
        queue.delete_entry(job["_id"])
        return
    current_attempts += 1
    max_attempts = 3
    if current_attempts >= max_attempts:
        print(f"Failed to process job after {current_attempts} attempts.")
        __save_to_db(endpoint, detail_id, data, status_code)
        queue.delete_entry(job["_id"])
        return
    print(f"{endpoint}: {detail_id} - Attempt {current_attempts}/{max_attempts} failed. Retrying...")
    queue.queue_collection.update_one(
        {"_id": job["_id"]}, {"$set": {"attempts": current_attempts, "last_processed": datetime.utcnow()}}
    )


def run():
    queue = RequestQueue()

    try:
        while True:
            start_time = time.time()
            job = queue.next(retry_interval_seconds=5)

            if job:
                try:
                    __process_job(job)
                except Exception as e:
                    print(f"Failed to process job: {e}")
            else:
                print("No jobs in the queue. Waiting...")

            elapsed_time = time.time() - start_time
            if elapsed_time < MAXIMUM_SLEEP:
                # Sleep for the remaining time to ensure 1 request per second
                time.sleep(MAXIMUM_SLEEP - elapsed_time)
    except KeyboardInterrupt:
        print("Keyboard interrupt. Closing queue...")
    finally:
        queue.connector.close()
        print("Queue closed.")
