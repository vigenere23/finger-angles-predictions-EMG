from abc import ABC, abstractmethod
from typing import Any, Union, Generic
from queue import Queue, Full
import multiprocessing
from src.utils.loggers import Logger
from src.utils.types import OutputType


class QueuePuttingStrategy(ABC):
    @abstractmethod
    def put(self, queue: Queue, data: Any):
        raise NotImplementedError()


class NonBlockingPut(QueuePuttingStrategy):
    def __init__(self, silence: bool, logger: Logger):
        self.__silence = silence
        self.__logger = logger

    def put(self, queue: Queue, data: Any):
        if self.__silence:
            try:
                queue.put_nowait(data)
            except Full:
                self.__logger.log('Queue full')
                pass
        else:
            queue.put_nowait(data)


class BlockingPut(QueuePuttingStrategy):
    def __init__(self, logger: Logger, silence: bool, timeout: float = None):
        self.__silence = silence
        self.__timeout = timeout
        self.__logger = logger

    def put(self, queue: Queue, data: Any):
        if self.__silence:
            try:
                queue.put(data, block=True, timeout=self.__timeout)
            except Full:
                self.__logger.log('Queue full')
                pass
        else:
            queue.put(data, block=True, timeout=self.__timeout)


class QueueFetchingStrategy(ABC, Generic[OutputType]):
    @abstractmethod
    def get(self, queue: Union[Queue, multiprocessing.Queue]) -> OutputType:
        raise NotImplementedError()


class BlockingMultiProcessFetch(QueueFetchingStrategy[OutputType]):
    def __init__(self, timeout: int = None):
        self.__timeout = timeout

    def get(self, queue: multiprocessing.Queue) -> OutputType:
        return queue.get(block = True, timeout = self.__timeout)
