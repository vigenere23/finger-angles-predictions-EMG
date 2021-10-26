from os import path, makedirs
import csv
from typing import Iterator
from src.utils.types import InputType
from src.data.handlers import DataHandler


class CSVSaver(DataHandler[InputType, InputType]):
    def __init__(self, file: str, batch_size: int) -> None:
        if not path.exists(path.dirname(file)):
            makedirs(path.dirname(file))

        self.__file = file
        self.__batch_size = batch_size
        self.__buffer = []

    def handle(self, input: Iterator[InputType]) -> Iterator[InputType]:
        for data in input:
            self.__buffer.append(data)

            if len(self.__buffer) == self.__batch_size:
                with open(self.__file, 'a+', newline='\n') as csvfile:
                    writer = csv.writer(csvfile, delimiter=';', quotechar='\\', quoting=csv.QUOTE_MINIMAL)
                    writer.writerows(self.__buffer)
                self.__buffer = []

            yield data
