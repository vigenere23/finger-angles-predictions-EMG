from abc import ABC, abstractmethod
from os import path, makedirs
import csv
from typing import Iterator, List, Optional
from src.pipeline.data import ProcessedData
from src.utils.types import InputType
from src.pipeline.handlers import DataHandler


class CSVSavingStrategy(ABC):
    @abstractmethod
    def create_header(self) -> Optional[List[str]]:
        raise NotImplementedError()

    @abstractmethod
    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        raise NotImplementedError()


class Complete(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return ['channel', 'timestamp', 'value']

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [
            data.channel,
            data.time,
            data.value
        ]


class ValueOnly(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return None

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [
            data.value
        ]


class WithoutChannel(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return ['timestamp', 'value']

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [
            data.time,
            data.value
        ]


class CSVWriter(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, file: str, batch_size: int, strategy: CSVSavingStrategy) -> None:
        self.__file = file
        self.__batch_size = batch_size
        self.__strategy = strategy

        self.__buffer = []

        if not path.exists(path.dirname(file)):
            makedirs(path.dirname(file))

        header = strategy.create_header()

        if header:
            self.__write_rows([header])


    def handle(self, input: Iterator[ProcessedData[InputType]]) -> Iterator[ProcessedData[InputType]]:
        for data in input:
            self.__buffer.append(self.__strategy.create_row(data))

            if len(self.__buffer) == self.__batch_size:
                self.__write_rows(self.__buffer)
                self.__buffer = []

            yield data


    def __write_rows(self, rows):
        with open(self.__file, 'a+', newline='\n') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='\\', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(rows)
