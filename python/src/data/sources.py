from datetime import datetime
from serial import Serial
import random
from abc import ABC, abstractmethod
from typing import Iterator, Generic
from src.data.data import SourceData
from src.utils.queues import NamedQueue, QueueFetchingStrategy
from src.utils.types import OutputType


class DataSource(ABC, Generic[OutputType]):
    @abstractmethod
    def get(self) -> Iterator[OutputType]:
        raise NotImplementedError()


class TestSource(DataSource[bytes]):
    def get(self) -> Iterator[bytes]:
        while True:
            data = b''
            for _ in range(10):
                data += b'\x00' + (random.randint(-15000, 15000)).to_bytes(2, 'little', signed=True) + b'\xFE'
            yield data


class SerialDataSource(DataSource[SourceData[bytes]]):
    def __init__(self, port: str, baudrate: int, start_byte: bytes, stop_byte: bytes, batch_size: int, message_size: int):
        serial = Serial(port=port, baudrate=baudrate)
        serial.reset_input_buffer()
        serial.reset_output_buffer()

        self.__serial = serial
        self.__start_byte = start_byte
        self.__stop_byte = stop_byte
        self.__batch_size = batch_size
        self.__message_size = message_size

    def get(self) -> Iterator[bytes]:
        start = datetime.now()

        self.__serial.inWaiting()
        self.__serial.read_until(self.__start_byte)
        data = self.__serial.read(self.__message_size * self.__batch_size - 1)
        data = self.__start_byte + data

        end = datetime.now()

        yield SourceData(
            value=data,
            start=start,
            end=end,
            start_byte=self.__start_byte,
            stop_byte=self.__stop_byte,
            message_size=self.__message_size,
            length=self.__batch_size,
        )


class QueueSource(DataSource[OutputType], Generic[OutputType]):
    def __init__(self, queue: NamedQueue, strategy: QueueFetchingStrategy):
        self.__queue = queue
        self.__strategy = strategy

    def get(self) -> Iterator[OutputType]:
        yield self.__strategy.get(self.__queue)
