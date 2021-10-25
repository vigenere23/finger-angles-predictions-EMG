from serial import Serial
import random
from abc import ABC, abstractmethod
from typing import Iterator, Generic
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


class SerialDataSource(DataSource[bytes]):
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
        self.__serial.inWaiting()
        self.__serial.read_until(self.__start_byte)
        data = self.__serial.read(self.__message_size * self.__batch_size - 1)
        data = self.__start_byte + data

        if not (self.verify_start_bytes(data) and self.verify_end_bytes(data)):
            raise RuntimeError("Corrupted data found... retrying")

        for x in zip(*(data[i::self.__message_size] for i in range(1, self.__message_size-1))):
            yield x

    def verify_start_bytes(self, data: bytes):
        return data[0::self.__message_size] == self.__start_byte * self.__batch_size

    def verify_end_bytes(self, data: bytes):
        return data[self.__message_size-1::self.__message_size] == self.__stop_byte * self.__batch_size


class QueueSource(DataSource[OutputType], Generic[OutputType]):
    def __init__(self, queue: NamedQueue, strategy: QueueFetchingStrategy):
        self.__queue = queue
        self.__strategy = strategy

    def get(self) -> Iterator[OutputType]:
        yield self.__strategy.get(self.__queue)
