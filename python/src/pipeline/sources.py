from datetime import datetime, timedelta
from serial import Serial
from random import randint
from time import sleep
from abc import ABC, abstractmethod
from typing import Iterator, Generic
from serial.serialutil import PARITY_NONE, PARITY_ODD
from src.pipeline.data import SourceData
from src.utils.loggers import Logger
from src.utils.queues import NamedQueue, QueueFetchingStrategy
from src.utils.types import OutputType


class DataSource(ABC, Generic[OutputType]):
    @abstractmethod
    def get(self) -> Iterator[OutputType]:
        raise NotImplementedError()


class FakeSerialSource(DataSource[SourceData[bytes]]):
    def __init__(self):
        self.__data_length = 32
        self.__message_length = 2
        self.__nb_channels = 2
        self.__dt = timedelta(milliseconds=10)

        self.__start = datetime.now()

    def __generate(self) -> bytes:
        return randint(-4000, 4000).to_bytes(2, 'big', signed=True)

    def get(self) -> Iterator[SourceData[bytes]]:
        end = self.__start + self.__dt

        yield SourceData(
            value=b''.join((self.__generate() for _ in range(self.__data_length))),
            start=self.__start,
            end=end,
            length=self.__data_length,
            message_length=self.__message_length,
            nb_channels=self.__nb_channels
        )

        self.__start = end

        sleep(self.__dt.total_seconds())


class SerialDataSource(DataSource[SourceData[bytes]]):
    def __init__(self, port: str, baudrate: int, sync_byte: bytes, check_byte: bytes, logger: Logger, use_parity: bool = False, verbose: bool = False):
        parity = PARITY_ODD if use_parity else PARITY_NONE
        serial = Serial(port=port, baudrate=baudrate, parity=parity)

        serial.reset_input_buffer()
        serial.reset_output_buffer()

        self.__serial = serial
        self.__sync_byte = sync_byte
        self.__check_byte = check_byte
        self.__logger = logger
        self.__verbose = verbose

    def get(self) -> Iterator[SourceData[bytes]]:
        self.__serial.inWaiting()

        start = datetime.now()
        self.__serial.read_until(self.__sync_byte)

        config = self.__serial.read(3)
        nb_channels = int(config[0])
        message_length = int(config[1])
        data_length = int(config[2])

        data = self.__serial.read(data_length)
        check_byte = self.__serial.read(1)

        end = datetime.now()

        if self.__verbose:
            self.__logger.log(f'config: {config} (channels: {nb_channels}, message_length: {message_length}, data_length: {data_length})')
            self.__logger.log(f'data: {data}')
            self.__logger.log(f'check: {check_byte}')

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