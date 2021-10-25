from abc import ABC, abstractmethod
from multiprocessing.context import Process
from threading import Thread
from typing import List
from src.data.sources import DataSource
from src.data.handlers import DataHandler


class Executor(ABC):
    @abstractmethod
    def execute(self):
        raise NotImplementedError()


class HandlersExecutor(Executor):
    def __init__(self, source: DataSource, handlers: List[DataHandler]) -> None:
        self.__source = source
        self.__handlers = handlers

    def execute(self):
        data = self.__source.get()
        for handler in self.__handlers:
            data = handler.handle(data)
        
        # triggers data execution
        for _ in data:
            pass


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
                print(f'### Exception ({e.__class__}) : {e}')
                print(e.with_traceback())

        if failed:
            raise RuntimeError('Maximum number of retries exceeded')


class ThreadsExecutor(Executor):
    def __init__(self, threads: List[Thread], wait_for_ending: bool) -> None:
        self.__threads = threads
        self.__wait_for_ending = wait_for_ending

    def execute(self):
        for thread in self.__threads:
            thread.start()

        if self.__wait_for_ending:
            for thread in self.__threads:
                thread.join()


class ProcessesExecutor(Executor):
    def __init__(self, processes: List[Process], wait_for_ending: bool) -> None:
        self.__processes = processes
        self.__wait_for_ending = wait_for_ending

    def execute(self):
        for process in self.__processes:
            process.start()

        if self.__wait_for_ending:
            for process in self.__processes:
                process.join()
