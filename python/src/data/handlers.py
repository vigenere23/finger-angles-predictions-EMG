import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, Iterator
from datetime import datetime
from queue import Queue
from dataclasses import replace
from src.data.data import ProcessedData, SourceData
from src.utils.lists import iter_groups
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
            channel = 0
            timestamps = np.linspace(data.start.timestamp(), data.end.timestamp(), data.length // data.message_length)
            data_groups = iter_groups(data.value, data.message_length)

            for timestamp, message in zip(timestamps, data_groups):
                yield ProcessedData(
                    time=timestamp,
                    channel=channel,
                    value=message,
                )
                channel = (channel + 1) % data.nb_channels


class ToInt(DataHandler[ProcessedData[bytes], ProcessedData[int]]):
    def handle(self, input: Iterator[ProcessedData[bytes]]) -> Iterator[ProcessedData[int]]:
        for data in input:
            new_value = int.from_bytes(bytearray(data.value), 'big', signed=True)
            yield replace(data, value=new_value)


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


class Plot(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, strategy: PlottingStrategy):
        self.__strategy = strategy

    def handle(self, input: Iterator[ProcessedData[InputType]]) -> Iterator[ProcessedData[InputType]]:
        for data in input:
            self.__strategy.update_plot(data.time, data.value)
            yield data


class ChannelSelector(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, channel: int) -> None:
        self.__channel = channel

    def handle(self, input: Iterator[ProcessedData[InputType]]) -> Iterator[ProcessedData[InputType]]:
        for data in input:
            if data.channel == self.__channel:
                yield data
