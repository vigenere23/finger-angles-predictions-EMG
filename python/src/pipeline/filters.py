from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Generic, List

from scipy import signal

from src.pipeline.data import ProcessedData
from src.pipeline.handlers import DataHandler
from src.utils.types import InputType, OutputType


class OfflineFilter(ABC, Generic[InputType, OutputType]):
    @abstractmethod
    def apply(self, data: List[InputType]) -> List[OutputType]:
        raise NotImplementedError()


class NotchFrequencyOffline(OfflineFilter[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, frequency: float, sampling_frequency: float):
        super().__init__()
        self.__b, self.__a = signal.iirnotch(Q=30, w0=frequency, fs=sampling_frequency)

    def apply(self, data: List[ProcessedData[int]]):
        values = map(lambda x: x.filtered, data)
        filtered = signal.filtfilt(b=self.__b, a=self.__a, x=values)
        return list(
            map(
                lambda original, filtered: replace(original, filtered=filtered),
                zip(data, filtered),
            )
        )


class NotchFrequencyOnline(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, frequency: float, sampling_frequency: float):
        self.__b, self.__a = signal.iirnotch(Q=30, w0=frequency, fs=sampling_frequency)
        self.__z = signal.lfilter_zi(self.__b, self.__a)

    def handle(self, input: ProcessedData[int]):
        filtered, self.__z = signal.lfilter(
            self.__b, self.__a, [input.filtered], zi=self.__z
        )
        self._next(replace(input, filtered=int(filtered)))


class NotchDC(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, R: float):
        super().__init__()
        self.__R = R
        self.__x1 = 0
        self.__y1 = 0

    def handle(self, input: ProcessedData[int]):
        y_n = int(input.filtered - self.__x1 + self.__R * self.__y1)

        self.__x1 = input.filtered
        self.__y1 = y_n

        self._next(replace(input, filtered=y_n))
