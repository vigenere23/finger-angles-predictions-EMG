import csv
from abc import ABC, abstractmethod
from os import makedirs, path
from typing import List, Optional

from modupipe.loader import Loader

from src.pipeline.data import ProcessedData
from src.utils.types import InputType

# TODO add tests


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
        return [str(data.channel), str(data.time), str(data.filtered)]


class ValueOnly(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return None

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [str(data.filtered)]


class WithoutChannel(CSVSavingStrategy):
    def create_header(self) -> Optional[List[str]]:
        return ["timestamp", "value"]

    def create_row(self, data: ProcessedData[InputType]) -> List[str]:
        return [str(data.time), str(data.filtered)]


class CSVWriter(Loader[ProcessedData[InputType, None]]):
    def __init__(self, file: str, batch_size: int, strategy: CSVSavingStrategy) -> None:
        super().__init__()
        self.__file = file
        self.__batch_size = batch_size
        self.__strategy = strategy

        self.__rows_buffer: List[List[str]] = []

        if not path.exists(path.dirname(file)):
            makedirs(path.dirname(file))

        header = strategy.create_header()

        if header:
            self.__write_rows([header])

    def load(self, item: ProcessedData[InputType]) -> None:
        self.__rows_buffer.append(self.__strategy.create_row(item))

        if len(self.__rows_buffer) == self.__batch_size:
            self.__write_rows(self.__rows_buffer)
            self.__rows_buffer = []

    def __write_rows(self, rows):
        with open(self.__file, "a+", newline="\n") as csvfile:
            writer = csv.writer(
                csvfile, delimiter=";", quotechar="\\", quoting=csv.QUOTE_MINIMAL
            )
            writer.writerows(rows)
