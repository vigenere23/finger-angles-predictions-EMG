from typing import List
from datetime import datetime
from src.data.executors.base import Executor, ExecutorFactory
from src.utils.loggers import ConsoleLogger
from src.utils.queues import NamedQueue


class QueuesAnalyzer(Executor):
    def __init__(self, queues: List[NamedQueue]) -> None:
        self.__queues = queues
        self.__start = datetime.now()
        self.__logger = ConsoleLogger(prefix='[queue usage]')

    def execute(self):
        now = datetime.now()
        if (now - self.__start).seconds >= 1:
            self.__start = now
            for queue in self.__queues:
                queue.print_usage(self.__logger)


class QueuesExecutorFactory(ExecutorFactory):
    def __init__(self, queues: List[NamedQueue]) -> None:
        self.__executor = QueuesAnalyzer(queues)

    def create(self) -> Executor:
        return self.__executor
