import multiprocessing
import queue
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, Union

from src.utils.loggers import Logger
from src.utils.types import OutputType


@dataclass
class NamedQueue:
    name: str
    queue: Union[multiprocessing.Queue, queue.Queue]
    maxsize: int = None

    def print_usage(self, logger: Logger):
        size = self.queue.qsize()

        if self.maxsize:
            total = self.maxsize
            logger.debug(f"{self.name} : {size}/{total} ({round(size/total*100, 2)}%)")
        else:
            logger.debug(f"{self.name} : {size}")


class QueuePuttingStrategy(ABC):
    @abstractmethod
    def put(self, queue: NamedQueue, data: Any):
        raise NotImplementedError()


class NonBlockingPut(QueuePuttingStrategy):
    def put(self, queue: NamedQueue, data: Any):
        queue.queue.put_nowait(data)


class BlockingPut(QueuePuttingStrategy):
    def __init__(self, timeout: float = None):
        self.__timeout = timeout

    def put(self, queue: NamedQueue, data: Any):
        queue.queue.put(data, block=True, timeout=self.__timeout)


class QueueFetchingStrategy(ABC, Generic[OutputType]):
    @abstractmethod
    def get(self, queue: NamedQueue) -> OutputType:
        raise NotImplementedError()


class BlockingFetch(QueueFetchingStrategy[OutputType]):
    def __init__(self, timeout: int = None):
        self.__timeout = timeout

    def get(self, queue: NamedQueue) -> OutputType:
        return queue.queue.get(block=True, timeout=self.__timeout)
