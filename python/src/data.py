from abc import ABC, abstractmethod
from typing import Any, List, Optional, Generic, Iterator
from serial import Serial
from src.types import InputData, OutputData
from src.filters import Filter


class DataSource(ABC, Generic[OutputData]):
    @abstractmethod
    def get(self) -> OutputData:
        raise NotImplementedError()

    def __next__(self) -> OutputData:
        return self.get()

    def __iter__(self) -> Iterator[OutputData]:
        yield next(self)


class SerialDataSource(DataSource[bytes]):
    def __init__(self, port: str, baudrate: int, start_bytes: bytes, stop_bytes: bytes):
        serial = Serial(port=port, baudrate=baudrate)
        serial.reset_input_buffer()
        serial.reset_output_buffer()

        self.__serial = serial
        self.__start_bytes = start_bytes
        self.__stop_bytes = stop_bytes

    def get(self) -> bytes:
        self.__serial.inWaiting()
        self.__serial.read_until(self.__start_bytes)
        data = self.__serial.read_until(self.__stop_bytes)

        return data[:-1]


class NonNullDataSource(DataSource[OutputData]):
    def __init__(self, source: DataSource[Optional[OutputData]]):
        self.__source = source
    
    def get(self) -> OutputData:
        data = self.__source.get()

        while not data:
            data = self.__source.get()

        return data


class FilteredDataSource(DataSource[OutputData], Generic[InputData, OutputData]):
    def __init__(self, source: DataSource[InputData], filters: List[Filter[Any, Any]] = []):
        self.__source = source
        self.__filters = filters

    def add_filter(self, filter):
        self.__filters.append(filter)

    def get(self) -> OutputData:
        data = self.__source.get()

        for filter in self.__filters:
            data = filter.apply(data)

        return data
