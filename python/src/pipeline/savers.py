import csv
from abc import ABC, abstractmethod
from os import makedirs, path
from typing import List, Optional

from src.pipeline.data import ProcessedData
from src.pipeline.handlers import DataHandler
from src.utils.types import InputType


class CSVSavingStrategy(ABC):
    @abstractmethod
    def create_header(self) -> Optional[List[str]]:
        raise NotImplementedError()

    @abstractmethod
    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        raise NotImplementedError()


class Complete(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return ["channel", "timestamp", "value"]

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [data.channel, data.time, data.filtered]


class ValueOnly(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return None

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [data.filtered]


class WithoutChannel(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return ["timestamp", "value"]

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [data.time, data.filtered]


class CSVWriter(DataHandler[ProcessedData[InputType], ProcessedData[InputType]]):
    def __init__(self, file: str, batch_size: int, strategy: CSVSavingStrategy) -> None:
        super().__init__()
        self.__file = file
        self.__batch_size = batch_size
        self.__strategy = strategy

        self.__buffer = []

        if not path.exists(path.dirname(file)):
            makedirs(path.dirname(file))

        header = strategy.create_header()

        if header:
            self.__write_rows([header])

    def handle(self, input: ProcessedData[InputType]) -> ProcessedData[InputType]:
        self.__buffer.append(self.__strategy.create_row(input))

        if len(self.__buffer) == self.__batch_size:
            self.__write_rows(self.__buffer)
            self.__buffer = []

        self._next(input)

    def __write_rows(self, rows):
        with open(self.__file, "a+", newline="\n") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=";", quotechar="\\", quoting=csv.QUOTE_MINIMAL
            )
            writer.writerows(rows)
