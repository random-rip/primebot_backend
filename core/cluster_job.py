import logging
from abc import abstractmethod
from typing import Any, Callable, Dict, Tuple, Union

from django_q.tasks import async_task


class Job:
    """
    Job class to inherit from for creating a job to be executed in a cluster.
    Call `.enqueue()` to push the job to the broker.
    """

    __name__ = 'Job'
    logger = logging.getLogger("qcluster")
    group = None

    @abstractmethod
    def function_to_execute(self) -> Callable:
        pass

    def kwargs(self) -> Dict:
        """
        `q_options` and `task_name` are reserved keywords from `async_task`, so these keys cannot be used!
        Returns: Keyword arguments for the `function_to_execute`
        """
        return {}

    def q_options(self) -> Dict[str, Any]:
        return {}

    def enqueue(self) -> Tuple[bool, Union[None, Any]]:
        """
        Create a Job for a cluster or execute sequentially if the cluster is not available.
        Returns (True, None) if the cluster is used else (False, None).
        Overwrite `_after_enqueue()` to return a custom return value as second value.

        Returns: A ``Tuple`` ( ``cluster_used``, ``object``).

        """
        self.logger.info("Creating new task...")
        q_options = {"group": self.__name__, **self.q_options()}
        try:
            task_id = async_task(self.function_to_execute(), **self.kwargs(), q_options=q_options)
            self.logger.info(f"Created task {task_id}...")
            return True, self._after_enqueue()
        except (Exception,) as e:
            self.logger.exception(e)
            self.logger.error(
                ("Could not connect to broker. Is the service running? " "Synchronous process started...")
            )
            async_task(self.function_to_execute(), **self.kwargs(), q_options={**q_options, "sync": True})
            return False, self._after_enqueue()

    def _after_enqueue(self) -> Any:
        return None


class SendMessageToDevsJob(Job):
    """
    Wrapper for creating an async task for Q cluster. Call `SendMessageToDevsJob(msg).enqueue()` to
    create an async_task.
    """

    __name__ = 'SendMessageToDevs'

    def function_to_execute(self) -> Callable:
        from bots.telegram_interface.tg_singleton import send_message_to_devs

        return send_message_to_devs

    def __init__(self, msg):
        self.msg = msg

    def kwargs(self) -> Dict:
        """
        `q_options` and `task_name` are reserved keywords from `async_task`, so these keys cannot be used!
        Returns: Keyword arguments for the `function_to_execute`
        """
        return {
            "msg": self.msg,
        }
