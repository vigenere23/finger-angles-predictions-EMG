from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod
from typing import Any, Generic, List
from datetime import datetime
from queue import Queue
from dataclasses import replace
from src.pipeline.data import ProcessedData, SourceData
from src.utils.lists import iter_groups
from src.utils.loggers import Logger
from src.utils.plot import PlottingStrategy
from src.utils.types import InputType, OutputType
from src.utils.queues import QueuePuttingStrategy


class DataHandler(ABC, Generic[InputType, OutputType]):
    def __init__(self):
        self.__next = None

    @abstractmethod
    def handle(self, input: InputType):
        raise NotImplementedError()

    def set_next(self, next: DataHandler[OutputType, Any]):
        self.__next = next

    def _next(self, output: OutputType):
        if self.__next:
            self.__next.handle(output)


class HandlersList(DataHandler[InputType, OutputType]):
    def __init__(self, handlers: List[DataHandler]):
        super().__init__()

        for i in range(len(handlers) - 1):
            handlers[i].set_next(handlers[i+1])

        self.__head = handlers[0]
        self.__tail = handlers[-1]
    
    def add_next(self, next: DataHandler):
        self.__tail.set_next(next)
        self.__tail = next

    def handle(self, input: InputType):
        self.__head.handle(input)
        self._next(input)


class Print(DataHandler[InputType, InputType]):
    def __init__(self, logger: Logger) -> None:
        super().__init__()
        self.__logger = logger

    def handle(self, input: InputType):
        self.__logger.log(input)
        self._next(input)


class ProcessFromUART(DataHandler[SourceData[bytes], ProcessedData[bytes]]):
    def handle(self, input: SourceData[bytes]):
        channel = 0
        timestamps = np.linspace(input.start.timestamp(), input.end.timestamp(), input.length // input.message_length)
        data_groups = iter_groups(input.value, input.message_length)

        for timestamp, message in zip(timestamps, data_groups):
            self._next(ProcessedData(
                time=timestamp,
                channel=channel,
                original=message,
                filtered=message,
            ))
            channel = (channel + 1) % input.nb_channels


class ToInt(DataHandler[ProcessedData[bytes], ProcessedData[int]]):
    def handle(self, input: ProcessedData[bytes]):
        new_value = int.from_bytes(bytearray(input.original), 'big', signed=True)
        self._next(replace(input, original=new_value, filtered=new_value))


class AddToQueue(DataHandler[InputType, InputType]):
    def __init__(self, queue: Queue, strategy: QueuePuttingStrategy) -> None:
        super().__init__()
        self.__queue = queue
        self.__strategy = strategy

    def handle(self, input: InputType):
        self.__strategy.put(self.__queue, input)
        self._next(input)


class Time(DataHandler[InputType, InputType]):
    def __init__(self, logger: Logger, timeout: int = 1) -> None:
        super().__init__()
        self.__start = datetime.now()
        self.__count = 0
        self.__logger = logger
        self.__timeout = timeout

    def handle(self, input: InputType):
        now = datetime.now()
        self.__count += 1

        if (now - self.__start).seconds >= self.__timeout:
            self.__logger.log(f'Rate : {round(self.__count/self.__timeout, 2)} / s')
            self.__count = 0
            self.__start = now

        self._next(input)


class Plot(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, strategy: PlottingStrategy):
        super().__init__()
        self.__strategy = strategy

    def handle(self, input: ProcessedData[InputType]):
        self.__strategy.update_plot(input.time, [input.original, input.filtered])
        self._next(input)


class Condition(ABC, Generic[InputType]):
    @abstractmethod
    def check(self, item: InputType) -> bool:
        raise NotImplementedError()


class ChannelSelection(Condition[ProcessedData]):
    def __init__(self, channel: int):
        super().__init__()
        self.__channel = channel

    def check(self, item: ProcessedData) -> bool:
        return item.channel == self.__channel


class ConditionalHandler(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, condition: Condition, handler: DataHandler) -> None:
        super().__init__()
        self.__condition = condition
        self.__conditional_handler = handler

    def handle(self, input: InputType):
        if self.__condition.check(input):
            self.__conditional_handler.handle(input)
        
        self._next(input)
