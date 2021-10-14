from abc import ABC, abstractmethod
from typing import Generic, Iterator, Tuple
import random
from datetime import datetime
from queue import Queue
from src.utils.loggers import Logger
from src.utils.plot import PlottingStrategy
from src.utils.types import InputType, OutputType
from src.utils.queues import QueuePuttingStrategy


class DataHandler(ABC, Generic[InputType, OutputType]):
    @abstractmethod
    def handle(self, input: Iterator[InputType]) -> Iterator[OutputType]:
        raise NotImplementedError()


class Print(DataHandler[InputType, InputType]):
    def __init__(self, logger: Logger) -> None:
        self.__logger = logger

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        for data in input:
            self.__logger.log(data)
            yield data


class Divider(DataHandler[InputType, InputType]):
    def handle(self, input: Iterator[InputType]) -> Iterator[OutputType]:
        for x in input:
            yield x/2


class Thrower(DataHandler[InputType, InputType]):
    def handle(self, input: Iterator[InputType]) -> Iterator[OutputType]:
        if random.random() > 0.95:    
            raise Exception('Fake exception')
        else:
            for data in input:
                yield data


class ToInt(DataHandler[bytes, int]):
    def handle(self, input: Iterator[bytes]) -> Iterator[int]:
        for data in input:
            yield int.from_bytes(bytearray(data), 'little', signed=True)


class Accumulator(DataHandler[InputType, InputType]):
    def __init__(self, size: int) -> None:
        self.__size = size

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        yield [next(input) for _ in range(self.__size)]


class AddTimestamp(DataHandler[InputType, Tuple[float, InputType]]):
    def handle(self, input: Iterator[InputType]) -> Iterator[Tuple[float, InputType]]:
        for data in input:
            now = datetime.now().timestamp()
            yield (now, data)


class AddToQueue(DataHandler[InputType, InputType]):
    def __init__(self, queue: Queue, strategy: QueuePuttingStrategy) -> None:
        self.__queue = queue
        self.__strategy = strategy

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        for data in input:
            self.__strategy.put(self.__queue, data)
            yield data


class Time(DataHandler[InputType, InputType]):
    def __init__(self, logger: Logger) -> None:
        self.__start = datetime.now()
        self.__count = 0
        self.__logger = logger

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        for data in input:
            now = datetime.now()
            self.__count += 1

            if (now - self.__start).seconds >= 1:
                self.__logger.log(f'Rate : {self.__count} / s')
                self.__count = 0
                self.__start = now

            yield data


class Plot(DataHandler[InputType, InputType]):
    def __init__(self, strategy: PlottingStrategy):
        self.__strategy = strategy

    def handle(self, input: Iterator[InputType]) -> Iterator[OutputType]:
        for data in input:
            self.__strategy.update_plot(data[0], data[1])
            yield data
