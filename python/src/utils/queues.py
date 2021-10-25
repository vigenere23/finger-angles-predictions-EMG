from abc import ABC, abstractmethod
from typing import Any, Union, Generic
import multiprocessing
import queue
from src.utils.types import OutputType


class NamedQueue:
    def __init__(self, name: str, maxsize: int, queue: Union[multiprocessing.Queue, queue.Queue]):
        self.queue = queue
        self.name = name
        self.maxsize = maxsize



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


class BlockingMultiProcessFetch(QueueFetchingStrategy[OutputType]):
    def __init__(self, timeout: int = None):
        self.__timeout = timeout

    def get(self, queue: NamedQueue) -> OutputType:
        return queue.queue.get(block = True, timeout = self.__timeout)
