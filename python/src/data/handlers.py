import numpy as np
from abc import ABC, abstractmethod
from typing import Any, Generic, Iterator, Tuple
from datetime import datetime
from queue import Queue
from src.data.data import ProcessedData, SourceData
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


class ProcessFromUART(DataHandler[SourceData[bytes], ProcessedData[bytes]]):
    def handle(self, input: Iterator[SourceData[bytes]]) -> Iterator[ProcessedData[bytes]]:
        for data in input:
            if not (self.verify_start_bytes(data) and self.verify_end_bytes(data)):
                raise RuntimeError("Corrupted data found... retrying")

            timestamps = np.linspace(data.start.timestamp(), data.end.timestamp(), data.length)
            data_extractor = (data.value[i::data.message_size] for i in range(1, data.message_size-1))
            for i, x in enumerate(zip(*data_extractor)):
                yield ProcessedData(
                    value=x,
                    time=datetime.fromtimestamp(timestamps[i])
                )

    def verify_start_bytes(self, data: SourceData[bytes]):
        return data.value[0::data.message_size] == data.start_byte * data.length

    def verify_end_bytes(self, data: SourceData[bytes]):
        return data.value[data.message_size-1::data.message_size] == data.stop_byte * data.length


class ToInt(DataHandler[ProcessedData[bytes], ProcessedData[int]]):
    def handle(self, input: Iterator[ProcessedData[bytes]]) -> Iterator[ProcessedData[int]]:
        for data in input:
            yield ProcessedData(
                value = int.from_bytes(bytearray(data.value), 'little', signed=True),
                time=data.time
            )


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
    def __init__(self, logger: Logger, timeout: int = 1) -> None:
        self.__start = datetime.now()
        self.__count = 0
        self.__logger = logger
        self.__timeout = timeout

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        for data in input:
            now = datetime.now()
            self.__count += 1

            if (now - self.__start).seconds >= self.__timeout:
                self.__logger.log(f'Rate : {round(self.__count/self.__timeout, 2)} / s')
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


class ToTuple(DataHandler[ProcessedData[InputType], Tuple[Any]]):
    def handle(self, input: Iterator[ProcessedData[InputType]]) -> Iterator[Tuple[Any]]:
        for data in input:
            yield data.to_tuple()
