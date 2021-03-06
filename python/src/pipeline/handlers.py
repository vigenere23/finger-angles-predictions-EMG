from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List
from datetime import datetime
from queue import Queue
from dataclasses import replace
from src.pipeline.data import ProcessedData, SourceData, RangeData
from src.pipeline.types import Animator, CharacteristicsExtractor, Model
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
    def __init__(self, logger: Logger, mapper = None) -> None:
        super().__init__()
        self.__logger = logger
        self.__mapper = mapper

    def handle(self, input: InputType):
        to_log = self.__mapper(input) if self.__mapper else input
        self.__logger.log(to_log)
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
    def __init__(self, condition: Condition, child: DataHandler) -> None:
        super().__init__()
        self.__condition = condition
        self.__child = child

    def handle(self, input: InputType):
        if self.__condition.check(input):
            self.__child.handle(input)
        
        self._next(input)


class TimeChecker(DataHandler):
    def __init__(self):
        super().__init__()
        self.__start = datetime.now()

    def handle(self, input: InputType):
        end = datetime.now()
        if (end - self.__start).seconds >= 1:
            self.__start = end
            print(end.timestamp())
        
        self._next(input)


class FixedAccumulator(DataHandler[ProcessedData[InputType], RangeData[InputType]]):
    def __init__(self, size: int):
        super().__init__()
        self.__size = size
        self.__buffer: List[ProcessedData[InputType]] = []
        self.__start: float = None

    def handle(self, input: ProcessedData[InputType]):
        if len(self.__buffer) == 0:
            self.__start = input.time

        self.__buffer.append(input.filtered)

        if len(self.__buffer) >= self.__size:
            output = RangeData(
                start = self.__start,
                end = input.time,
                value = self.__buffer
            )
            self._next(output)
            self.__buffer = []


class FixedRangeAccumulator(DataHandler[RangeData[InputType], RangeData[List[InputType]]]):
    def __init__(self, size: int):
        super().__init__()
        self.__size = size
        self.__buffer: List[ProcessedData[InputType]] = []
        self.__start: float = None

    def handle(self, input: RangeData[InputType]):
        if len(self.__buffer) == 0:
            self.__start = input.start

        self.__buffer.append(input.value)

        if len(self.__buffer) >= self.__size:
            output = RangeData(
                start = self.__start,
                end = input.end,
                value = self.__buffer
            )
            self._next(output)
            self.__buffer = []


class TimedAccumulator(DataHandler[ProcessedData[InputType], RangeData[List[InputType]]]):
    def __init__(self, time_in_seconds: float):
        super().__init__()
        self.__time_in_seconds = time_in_seconds
        self.__buffer = []
        self.__start: float = None

    def handle(self, input: ProcessedData[InputType]):
        if len(self.__buffer) == 0:
            self.__start = input.time

        self.__buffer.append(input.filtered)

        if input.time >= self.__start + self.__time_in_seconds:
            output = RangeData(
                start = self.__start,
                end = input.time,
                value = self.__buffer
            )
            self._next(output)
            self.__buffer = []


class ToNumpy(DataHandler[RangeData[InputType], RangeData[np.ndarray]]):
    def __init__(self, flatten: bool = False, to2D: bool = False):
        self.__flatten = flatten
        self.__to2D = False if self.__flatten else to2D

    def handle(self, input: RangeData[InputType]):
        output = np.array(input.value)

        if self.__flatten:
            output = output.flatten()

        if self.__to2D:
            output = np.array([output])

        self._next(replace(
            input,
            value = output
        ))


class ExtractCharacteristics(DataHandler[RangeData[np.ndarray], RangeData[np.ndarray]]):
    def __init__(self, extractor: CharacteristicsExtractor):
        super().__init__()
        self.__extractor = extractor
    
    def handle(self, input: RangeData[List[int]]):
        output = self.__extractor.extract(input.value)
        self._next(replace(
            input,
            value = output
        ))


class Predict(DataHandler[RangeData[np.ndarray], RangeData[np.ndarray]]):
    def __init__(self, model: Model):
        super().__init__()
        self.__model = model

    def handle(self, input: RangeData[np.ndarray]):
        output = self.__model.predict(input.value)
        self._next(replace(
            input,
            value = output
        ))


class Animate(DataHandler[RangeData[np.ndarray], RangeData[np.ndarray]]):
    def __init__(self, animator: Animator):
        super().__init__()
        self.__animator = animator

    def handle(self, input: RangeData[np.ndarray]):
        self.__animator.animate(input)
        self._next(input)
