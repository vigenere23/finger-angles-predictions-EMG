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
    def __init__(self, port: str, baudrate: int, sync_byte: bytes, check_byte: bytes):
        serial = Serial(port=port, baudrate=baudrate)
        serial.reset_input_buffer()
        serial.reset_output_buffer()

        self.__serial = serial
        self.__sync_byte = sync_byte
        self.__check_byte = check_byte

    def get(self) -> Iterator[bytes]:
        self.__serial.inWaiting()
        self.__serial.read_until(self.__sync_byte)

        start = datetime.now()

        config = self.__serial.read(3)
        nb_channels = int(config[0])
        message_length = int(config[1])
        data_length = int(config[2])

        data = self.__serial.read(data_length)
        check_byte = self.__serial.read(1)

        end = datetime.now()

        if check_byte != self.__check_byte:
            raise RuntimeError('Did not received the expected UART packet')

        yield SourceData(
            value=data,
            start=start,
            end=end,
            nb_channels=nb_channels,
            length=data_length,
            message_length=message_length,
        )


class QueueSource(DataSource[OutputType], Generic[OutputType]):
    def __init__(self, queue: NamedQueue, strategy: QueueFetchingStrategy):
        self.__queue = queue
        self.__strategy = strategy

    def get(self) -> Iterator[OutputType]:
        yield self.__strategy.get(self.__queue)
