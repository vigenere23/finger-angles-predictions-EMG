from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        raise NotImplementedError()


class ConsoleLogger(Logger):
    def __init__(self, prefix: str = '') -> None:
        self.__prefix = prefix

    def log(self, message: str) -> None:
        print(f'{self.__prefix} {message}')
