from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def debug(self, text: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def info(self, text: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def warning(self, text: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def error(self, text: str) -> None:
        raise NotImplementedError()


class ConsoleLogger(Logger):
    def __init__(self, name: str = "") -> None:
        self.name = name

    def debug(self, text: str) -> None:
        print(f"[DEBUG]-[{self.name}] {text}")

    def info(self, text: str) -> None:
        print(f"[INFO]-[{self.name}] {text}")

    def warning(self, text: str) -> None:
        print(f"[WARNING]-[{self.name}] {text}")

    def error(self, text: str) -> None:
        print(f"[ERROR]-[{self.name}] {text}")
