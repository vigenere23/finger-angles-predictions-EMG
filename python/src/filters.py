from abc import ABC, abstractmethod
from typing import Optional, Generic
import struct
from numpy import cos
from src.utils import SizedFifo
from src.types import InputData, OutputData


class Filter(ABC, Generic[InputData, OutputData]):
    @abstractmethod
    def apply(self, data: InputData) -> OutputData:
        raise NotImplementedError()


class BytesToInt(Filter[bytes, Optional[int]]):
    def apply(self, data: bytes) -> Optional[int]:
        try:
            unpacked = struct.unpack('>H', data)
            return unpacked[0]
        except struct.error:
            print(f'Failed to convert bytes message {data} to integer')
            return None


class LowPassIIR(Filter[int, int]):
    def __init__(self, window_size: int):
        self.__N = window_size
        self.__x_history = SizedFifo[int](window_size)
        self.__y_nm1 = 0

    def apply(self, data: int) -> int:
        y_n = int(
            (
                self.__y_nm1 * self.__N \
                + data \
                - self.__x_history.oldest()
            ) / self.__N
        )

        self.__x_history.append(data)
        self.__y_nm1 = y_n

        return y_n


class NotchDC(Filter[int, int]):
    def __init__(self, R: float):
        self.__R = R
        self.__x_nm1 = 0
        self.__y_nm1 = 0

    def apply(self, data: int) -> int:
        y_n = int(
            data - self.__x_nm1 \
            + self.__R * self.__y_nm1
        )

        self.__x_nm1 = data
        self.__y_nm1 = y_n

        return y_n


class NotchFrequency(Filter[int, int]):
    def __init__(self, R: float, frequency: float, frequency_range: float):
        wn = frequency / (frequency_range / 2)
        self.__R = R
        self.__R_square = R**2
        self.__cos_wn = cos(wn)

        self.__x_nm1 = 0
        self.__y_nm1 = 0
        self.__x_nm2 = 0
        self.__y_nm2 = 0

    def apply(self, data: int) -> int:
        y_n = int(
            data \
            - 2 * self.__cos_wn * self.__x_nm1 \
            + self.__x_nm2 \
            + 2 * self.__R * self.__cos_wn * self.__y_nm1 \
            - self.__R_square * self.__y_nm2
        )

        self.__x_nm1 = data
        self.__y_nm1 = y_n
        self.__x_nm2 = self.__x_nm1
        self.__y_nm2 = self.__y_nm1

        return y_n