from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import pi, sin
from random import randint
from time import sleep
from typing import Iterator, List

from modupipe.source import Source
from serial import Serial
from serial.serialutil import PARITY_NONE, PARITY_ODD

from src.pipeline.data import SerialData
from src.utils.loggers import ConsoleLogger, Logger


@dataclass
class FrequencyConfig:
    amplitude: float
    frequency: float
    offset: float


class SerialSource(Source[SerialData[bytes]], ABC):
    pass


class RandomSerialSource(Source[SerialData[bytes]]):
    def __init__(self):
        self.__data_length = 32
        self.__message_length = 2
        self.__nb_channels = 2
        self.__dt = timedelta(milliseconds=10)

        self.__start = datetime.now()

    def __generate(self) -> bytes:
        return randint(-4000, 4000).to_bytes(2, "big", signed=True)

    def fetch(self) -> Iterator[SerialData[bytes]]:
        end = self.__start + self.__dt

        yield SerialData(
            value=b"".join((self.__generate() for _ in range(self.__data_length))),
            start=self.__start,
            end=end,
            length=self.__data_length,
            message_length=self.__message_length,
            nb_channels=self.__nb_channels,
        )

        self.__start = end

        sleep(self.__dt.total_seconds())


class FrequencySource(Source[SerialData[bytes]]):
    def __init__(self, configs: List[FrequencyConfig]):
        self.__data_length = 256
        self.__message_length = 2
        self.__nb_channels = 2
        self.__sample_rate = 2500
        self.__configs = configs

        self.__sample_dt = timedelta(seconds=1 / self.__sample_rate)
        self.__sleep_dt = timedelta(
            seconds=(self.__data_length + 5)
            / (self.__sample_rate * 2 * self.__nb_channels)
        )
        self.__start = datetime.now()

    def __generate(self, t: float) -> bytes:
        data = 0.0
        for config in self.__configs:
            data += config.offset + config.amplitude * sin(
                2.0 * pi * config.frequency * t
            )

        return int(data).to_bytes(2, "big", signed=True)

    def fetch(self) -> Iterator[SerialData[bytes]]:
        delay_start = datetime.now()
        data: List[bytes] = []
        end = self.__start

        for _ in range(self.__data_length // 2 // self.__nb_channels):
            value = self.__generate(end.timestamp())
            data.extend((value for _ in range(self.__nb_channels)))
            end += self.__sample_dt

        joined_data = b"".join(data)

        yield SerialData(
            value=joined_data,
            start=self.__start,
            end=end - self.__sample_dt,
            length=self.__data_length,
            message_length=self.__message_length,
            nb_channels=self.__nb_channels,
        )

        self.__start = end

        delay = datetime.now() - delay_start
        sleep((self.__sleep_dt - delay).total_seconds())


class BaseSerialSource(Source[SerialData[bytes]]):
    def __init__(
        self,
        port: str,
        baudrate: int,
        sync_byte: bytes,
        check_byte: bytes,
        logger: Logger,
        use_parity: bool = False,
        verbose: bool = False,
    ):
        parity = PARITY_ODD if use_parity else PARITY_NONE
        serial = Serial(port=port, baudrate=baudrate, parity=parity)

        serial.reset_input_buffer()
        serial.reset_output_buffer()

        if serial.in_waiting:
            serial.read(serial.in_waiting)

        self.__serial = serial
        self.__sync_byte = sync_byte
        self.__check_byte = check_byte
        self.__logger = logger
        self.__verbose = verbose

    def fetch(self) -> Iterator[SerialData[bytes]]:
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
            self.__logger.log(
                f"config: {config} (channels: {nb_channels}, message_length: {message_length}, data_length: {data_length})"
            )
            self.__logger.log(f"data: {data}")
            self.__logger.log(f"check: {check_byte}")

        if check_byte != self.__check_byte:
            raise RuntimeError("Did not received the expected UART packet")

        yield SerialData(
            value=data,
            start=start,
            end=end,
            nb_channels=nb_channels,
            length=data_length,
            message_length=message_length,
        )


class SerialSourceFactory:
    def create(self, port: str) -> SerialSource:
        logger = ConsoleLogger(prefix="[serial]")

        if port == "rand":
            return RandomSerialSource()
        elif "freq" in port:
            try:
                configs = []
                for config in port.split(":")[1].split("_"):
                    amp, freq, offset = config.split("-")
                    configs.append(
                        FrequencyConfig(
                            amplitude=float(amp),
                            frequency=float(freq),
                            offset=float(offset),
                        )
                    )
                return FrequencySource(configs=configs)
            except KeyError:
                raise ValueError(
                    "format should be 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>'"
                )
        else:
            return SerialSource(
                port=port,
                baudrate=115200,
                sync_byte=b"\n",
                check_byte=b"\xFF",
                logger=logger,
                # verbose=True
            )
