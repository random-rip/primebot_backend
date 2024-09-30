from request_queue import EndpointType, RequestQueue
from request_queue.mongo import mongo_connector


def push(endpoint: EndpointType, detail_id: int, priority: int = 0) -> str:
    """
    Push a job to the request queue.
    :param endpoint:
    :param detail_id:
    :param priority:
    :return: the job id
    """
    q = RequestQueue(connector=mongo_connector)
    return q.push(endpoint, detail_id, priority)
