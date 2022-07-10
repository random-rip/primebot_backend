import logging
from abc import abstractmethod
from typing import Any, Tuple, Union, Callable

import redis
from django_q.tasks import async_task


class AsyncWrapper:
    __name__ = 'AsyncWrapper'
    logger = logging.getLogger("django")
    group = None

    @abstractmethod
    def function_to_execute(self) -> Callable:
        pass

    def arguments(self) -> Tuple:
        return (),

    @property
    def q_options(self):
        return {
            "task_name": self.__name__,
        }

    def enqueue(self) -> Tuple[bool, Union[None, Any]]:
        """
        Create a Task for Q Cluster or execute sequentially if the cluster is not available.
        Returns (True, None) if the cluster is used else (False, None).
        Overwrite `_after_enqueue()` to return a custom return value as second parameter.

        Returns: A ``Tuple`` (cluster_used, `object`).

        """
        self.logger.info("Creating new task...")
        try:
            task_id = async_task(self.function_to_execute(), *self.arguments(), q_options=self.q_options)
            self.logger.info(f"Created task {task_id}...")
            return True, self._after_enqueue()
        except (redis.exceptions.ConnectionError, Exception) as e:
            self.logger.exception(e)
            self.logger.error((
                "Could not connect to Redis Server. Is the service Running? "
                "Synchronous process started..."
            ))
            self.function_to_execute()(*self.arguments())

        return False, self._after_enqueue()

    def _after_enqueue(self) -> Any:
        return None
