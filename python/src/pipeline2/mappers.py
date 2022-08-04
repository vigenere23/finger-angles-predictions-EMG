from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Iterator

import numpy as np
from modupipe.mapper import Mapper
from scipy import signal

from src.pipeline.data import ProcessedData, SerialData
from src.utils.lists import iter_groups
from src.utils.loggers import Logger
from src.utils.types import InputType, OutputType


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


class Log(Mapper[InputType, InputType]):
    def __init__(self, logger: Logger, mapper=None) -> None:
        super().__init__()
        self.__logger = logger
        self.__mapper = mapper

    def map(self, items: Iterator[InputType]) -> Iterator[InputType]:
        for item in items:
            to_log = self.__mapper(item) if self.__mapper else item
            self.__logger.debug(to_log)
            yield item


class ProcessFromSerial(Mapper[SerialData[bytes], ProcessedData[bytes]]):
    def map(self, items: Iterator[SerialData[bytes]]) -> Iterator[ProcessedData[bytes]]:
        for item in items:
            channel = 0
            timestamps = np.linspace(
                item.start.timestamp(),
                item.end.timestamp(),
                item.length // item.message_length,
            )
            data_groups = iter_groups(list(item.value), item.message_length)

            for timestamp, message in zip(timestamps, data_groups):
                yield ProcessedData(
                    time=timestamp,
                    channel=channel,
                    original=bytes(message),
                    filtered=bytes(message),
                )
                channel = (channel + 1) % item.nb_channels


class ToInt(Mapper[ProcessedData[bytes], ProcessedData[int]]):
    def map(
        self, items: Iterator[ProcessedData[bytes]]
    ) -> Iterator[ProcessedData[int]]:
        for item in items:
            new_value = int.from_bytes(bytearray(item.original), "big", signed=True)
            yield ProcessedData(
                time=item.time,
                channel=item.channel,
                original=new_value,
                filtered=new_value,
            )


class NotchFrequencyOnline(Mapper[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, frequency: float, sampling_frequency: float):
        self.__b, self.__a = signal.iirnotch(Q=30, w0=frequency, fs=sampling_frequency)
        self.__z = signal.lfilter_zi(self.__b, self.__a)

    def map(self, items: Iterator[ProcessedData[int]]) -> Iterator[ProcessedData[int]]:
        for item in items:
            filtered, self.__z = signal.lfilter(
                self.__b, self.__a, [item.filtered], zi=self.__z
            )
            yield ProcessedData(
                time=item.time,
                channel=item.channel,
                original=item.original,
                filtered=filtered,
            )


class NotchDC(Mapper[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, R: float):
        super().__init__()
        self.__R = R
        self.__x1 = 0
        self.__y1 = 0

    def map(self, items: Iterator[ProcessedData[int]]) -> Iterator[ProcessedData[int]]:
        for item in items:
            y_n = int(item.filtered - self.__x1 + self.__R * self.__y1)

            self.__x1 = item.filtered
            self.__y1 = y_n

            yield ProcessedData(
                time=item.time,
                channel=item.channel,
                original=item.original,
                filtered=y_n,
            )
