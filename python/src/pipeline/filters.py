from dataclasses import replace
from typing import Iterator
from numpy import cos, pi
from src.pipeline.data import ProcessedData

from src.pipeline.handlers import DataHandler


# class LowPassIIR(Filter[int]):
#     def __init__(self, window_size: int):
#         self.__N = window_size
#         self.__x_history = SizedFifo[int](window_size)
#         self.__y_nm1 = 0

#     def apply(self, data: int) -> int:
#         y_n = int(
#             (
#                 self.__y_nm1 * self.__N \
#                 + data \
#                 - self.__x_history.oldest()
#             ) / self.__N
#         )

#         self.__x_history.append(data)
#         self.__y_nm1 = y_n

#         return y_n


# class NotchDC(Filter[int]):
#     def __init__(self, R: float):
#         super().__init__()
#         self.__R = R
#         self.__x_nm1 = 0
#         self.__y_nm1 = 0

#     def apply(self, data: int) -> int:
#         y_n = int(
#             data - self.__x_nm1 \
#             + self.__R * self.__y_nm1
#         )

#         self.__x_nm1 = data
#         self.__y_nm1 = y_n

#         return y_n


class NotchFrequency(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, R: float, frequency: float, sampling_frequency: float):
        wn = 2 * frequency / sampling_frequency
        self.__R = R
        self.__R_square = R**2
        self.__cos_wn = cos(wn)

        self.__x_nm1 = 0
        self.__y_nm1 = 0
        self.__x_nm2 = 0
        self.__y_nm2 = 0

    def handle(self, input: Iterator[ProcessedData[int]]) -> Iterator[ProcessedData[int]]:
        for data in input:
            y_n = int(
                data.value \
                - 2 * self.__cos_wn * self.__x_nm1 \
                + self.__x_nm2 \
                + 2 * self.__R * self.__cos_wn * self.__y_nm1 \
                - self.__R_square * self.__y_nm2
            )

            self.__x_nm1 = data.value
            self.__y_nm1 = y_n
            self.__x_nm2 = self.__x_nm1
            self.__y_nm2 = self.__y_nm1

            yield replace(data, value=y_n)
