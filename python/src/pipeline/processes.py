import time
from multiprocessing import Process

from src.pipeline.executors.base import Executor


class ExecutorProcess(Process):
    def __init__(self, name: str, executor: Executor) -> None:
        super().__init__(name=name)
        self.__executor = executor

    def run(self) -> None:
        while True:
            self.__executor.execute()


class SleepingExecutorProcess(Process):
    def __init__(self, name: str, executor: Executor, sleep_time: float) -> None:
        super().__init__(name=name)
        self.__executor = executor
        self.__sleep_time = sleep_time

    def run(self) -> None:
        while True:
            self.__executor.execute()
            time.sleep(self.__sleep_time)
