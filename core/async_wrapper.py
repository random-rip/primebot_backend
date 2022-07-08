import logging
from abc import abstractmethod
from typing import Any, Tuple, Union

import redis
from django.conf import settings
from django_q.tasks import async_task


class AsyncWrapper:
    __name__ = 'AsyncWrapper'
    logger = logging.getLogger("django")

    @abstractmethod
    def _process(self) -> None:
        pass

    def enqueue(self) -> Tuple[bool, Union[None, Any]]:
        """
        Create a Task for Q Cluster or execute sequentially if the cluster is not available.
        Returns (True, None) if the cluster is used else (False, None).
        Overwrite `_after_enqueue()` to return a custom return value as second parameter.

        Returns: A ``Tuple`` (cluster_used, `object`).

        """
        self.logger.info("Creating new task...")
        if settings.USE_Q_CLUSTER:
            try:
                task_id = async_task(self._process, )
                self.logger.info(f"Created task {task_id}...")
                return True, self._after_enqueue()
            except (redis.exceptions.ConnectionError, Exception) as e:
                self.logger.exception(e)
                self.logger.error((
                    "Could not connect to Redis Server. Is the service Running? "
                    "Synchronous process started..."
                ))
                self._process()
        else:
            self._process()

        return False, self._after_enqueue()

    def _after_enqueue(self) -> Any:
        return None
