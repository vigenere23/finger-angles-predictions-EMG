from multiprocessing import Process
from threading import Thread
from time import sleep
from src.data.executors import Executor


class ExecutorThread(Thread):
    def __init__(self, name: str, executor: Executor, sleep_time: float) -> None:
        super().__init__(name=name)
        self.__executor = executor
        self.__sleep_time = sleep_time

    def run(self) -> None:
        while True:
            self.__executor.execute()
            sleep(self.__sleep_time)


class ExecutorProcess(Process):
    def __init__(self, name: str, executor: Executor) -> None:
        super().__init__(name=name)
        self.__executor = executor
    
    def run(self) -> None:
        while True:
            self.__executor.execute()
