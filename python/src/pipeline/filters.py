from dataclasses import replace
from typing import List
from numpy import cos, pi
from src.pipeline.data import ProcessedData
from src.pipeline.handlers import DataHandler
from scipy.signal import iirnotch, filtfilt


class NotchFrequency(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, R: float, frequency: float, sampling_frequency: float):
        super().__init__()

        wn = pi * frequency / sampling_frequency

        self.__R = R
        self.__R_square = R**2
        self.__cos_wn = cos(wn)

        self.__x_nm1 = 0
        self.__y_nm1 = 0
        self.__x_nm2 = 0
        self.__y_nm2 = 0

    def handle(self, input: ProcessedData[int]):
        y_n = int(
            input.filtered \
            - 2 * self.__cos_wn * self.__x_nm1 \
            + self.__x_nm2 \
            + 2 * self.__R * self.__cos_wn * self.__y_nm1 \
            - self.__R_square * self.__y_nm2
        )

        self.__x_nm1 = input.filtered
        self.__y_nm1 = y_n
        self.__x_nm2 = self.__x_nm1
        self.__y_nm2 = self.__y_nm1

        self._next(replace(input, filtered=y_n))

    def coefficients(self):
        return [1, -2 * self.__cos_wn, 1], [1, -2 * self.__R * self.__cos_wn, self.__R_square]
        # return [1, -2, 1], [1, -2 * self.__R, 1]


class NotchFrequency2(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, BW: float, frequency: float, sampling_frequency: float):
        super().__init__()

        wn = 2 * pi * frequency / sampling_frequency
        cos_wn = cos(wn)
        R = 1 - 3 * BW / sampling_frequency
        R_square = R**2
        K = (1 - 2 * R * cos_wn + R_square) / (2 - 2 * cos_wn)

        self.__a0 = 1 - K
        self.__a1 = -2 * K * cos_wn
        self.__a2 = K
        self.__b1 = 2 * R * cos_wn
        self.__b2 = R_square

        self.__x1 = 0
        self.__y1 = 0
        self.__x2 = 0
        self.__y2 = 0

    def handle(self, input: ProcessedData[int]):
        y_n = int(
            self.__a0 * input.filtered \
            + self.__a1 * self.__x1 \
            + self.__a2 * self.__x2 \
            + self.__b1 * self.__y1 \
            + self.__b2 * self.__y2
        )
        y_n = max(-400, y_n)
        y_n = min(400, y_n)

        self.__x1 = input.filtered
        self.__y1 = y_n
        self.__x2 = self.__x1
        self.__y2 = self.__y1

        self._next(replace(input, filtered=y_n))


class NotchFrequencyScipy(DataHandler[ProcessedData[int], ProcessedData[int]]):
    def __init__(self, frequency: float, sampling_frequency: float):
        super().__init__()
        self.__b, self.__a = iirnotch(Q=30, w0=frequency, fs=sampling_frequency)
        self.__batch: List[ProcessedData[int]] = []
        self.__to_filter: List[int] = []

    def handle(self, input: ProcessedData[int]):
        self.__batch.append(input)
        self.__to_filter.append(input.filtered)

        if len(self.__batch) == 1000:
            filtered = filtfilt(b=self.__b, a=self.__a, x=self.__to_filter)
            
            for input, new_value in zip(self.__batch, filtered):
                self._next(replace(input, filtered=int(new_value)))
            self.__batch = []
            self.__to_filter = self.__to_filter[-2:]


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
