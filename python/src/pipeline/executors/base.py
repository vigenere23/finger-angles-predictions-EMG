import traceback
from abc import ABC, abstractmethod
from multiprocessing.context import Process
from typing import List

from src.pipeline.handlers import DataHandler
from src.pipeline.sources import DataSource


class Executor(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError()


class ExecutorFactory(ABC):
    @abstractmethod
    def create(self) -> Executor:
        raise NotImplementedError()


class FromSourceExecutor(Executor):
    def __init__(self, source: DataSource, handler: DataHandler) -> None:
        self.__source = source
        self.__handler = handler

    def execute(self):
        data = self.__source.get()
        for input in data:
            self.__handler.handle(input)


class Retryer(Executor):
    def __init__(self, executor: Executor, nb_retries: int) -> None:
        self.__executor = executor
        self.__nb_retries = nb_retries

    def execute(self):
        failed = True
        for _ in range(self.__nb_retries):
            try:
                self.__executor.execute()
                failed = False
                break
            except Exception as e:
                print(f"### Exception ({e.__class__}) : {e}")
                print(traceback.format_exc())

        if failed:
            raise RuntimeError("Maximum number of retries exceeded")


class ProcessesExecutor(Executor):
    def __init__(self, processes: List[Process]) -> None:
        self.__processes = processes

    def execute(self):
        for process in self.__processes:
            process.start()
            print(f"Started > {process.name}")
