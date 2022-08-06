from __future__ import annotations

from typing import Iterator, List

import numpy as np
from modupipe.mapper import Mapper
from scipy import signal

from src.pipeline.data import ProcessedData, RangeData, SerialData
from src.pipeline.types import CharacteristicsExtractor, PredictionModel
from src.utils.lists import iter_groups
from src.utils.loggers import Logger
from src.utils.types import InputType


class Log(Mapper[InputType, InputType]):
    def __init__(self, logger: Logger, mapper=None) -> None:
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
        self.b, self.a = signal.iirnotch(Q=30, w0=frequency, fs=sampling_frequency)
        self.z = signal.lfilter_zi(self.b, self.a)

    def map(self, items: Iterator[ProcessedData[int]]) -> Iterator[ProcessedData[int]]:
        for item in items:
            filtered, self.z = signal.lfilter(
                self.b, self.a, [item.filtered], zi=self.z
            )
            yield ProcessedData(
                time=item.time,
                channel=item.channel,
                original=item.original,
                filtered=filtered,
            )


class NotchDC(Mapper[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, R: float):
        self.R = R
        self.x1 = 0
        self.y1 = 0

    def map(self, items: Iterator[ProcessedData[int]]) -> Iterator[ProcessedData[int]]:
        for item in items:
            filtered = int(item.filtered - self.x1 + self.R * self.y1)

            self.x1 = item.filtered
            self.y1 = filtered

            yield ProcessedData(
                time=item.time,
                channel=item.channel,
                original=item.original,
                filtered=filtered,
            )


class TimedBuffer(Mapper[ProcessedData[InputType], RangeData[List[InputType]]]):
    def __init__(self, time_in_seconds: float):
        super().__init__()
        self.time_in_seconds = time_in_seconds
        self.buffer: List[InputType] = []
        self.start: float = 0

    def map(
        self, items: Iterator[ProcessedData[InputType]]
    ) -> Iterator[RangeData[List[InputType]]]:
        for item in items:
            if len(self.buffer) == 0:
                self.start = item.time

            self.buffer.append(item.filtered)

            if item.time >= self.start + self.time_in_seconds:
                output = RangeData(start=self.start, end=item.time, value=self.buffer)
                yield output
                self.buffer = []


class ToNumpy(Mapper[RangeData[InputType], RangeData[np.ndarray]]):
    def __init__(self, flatten: bool = False, to2D: bool = False):
        self.flatten = flatten
        self.to2D = False if self.flatten else to2D

    def map(
        self, items: Iterator[RangeData[InputType]]
    ) -> Iterator[RangeData[np.ndarray]]:
        for item in items:
            output = np.array(item.value)

            if self.flatten:
                output = output.flatten()

            if self.to2D:
                output = np.array([output])

            yield RangeData(start=item.start, end=item.end, value=output)


class ExtractCharacteristics(Mapper[RangeData[np.ndarray], RangeData[np.ndarray]]):
    def __init__(self, extractor: CharacteristicsExtractor):
        self.extractor = extractor

    def map(
        self, items: Iterator[RangeData[np.ndarray]]
    ) -> Iterator[RangeData[np.ndarray]]:
        for item in items:
            characteristics = self.extractor.extract(item.value)

            yield RangeData(start=item.start, end=item.end, value=characteristics)


class Predict(Mapper[RangeData[np.ndarray], RangeData[np.ndarray]]):
    def __init__(self, model: PredictionModel):
        self.model = model

    def map(
        self, items: Iterator[RangeData[np.ndarray]]
    ) -> Iterator[RangeData[np.ndarray]]:
        for item in items:
            prediction = self.model.predict(item.value)

            yield RangeData(
                start=item.start,
                end=item.end,
                value=prediction,
            )


class MergeRangeData(Mapper[List[RangeData[np.ndarray]], RangeData[List[np.ndarray]]]):
    def map(
        self, items: Iterator[List[RangeData[np.ndarray]]]
    ) -> Iterator[RangeData[List[np.ndarray]]]:
        for items_list in items:
            values = [item.value for item in items_list]
            start = min(map(lambda item: item.start, items_list))
            end = min(map(lambda item: item.end, items_list))

            yield RangeData(start=start, end=end, value=values)
