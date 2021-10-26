from abc import ABC, abstractmethod
from os import path
from pathlib import Path
from datetime import datetime
from typing import List
from src.data.savers import CSVSaver
from src.utils.loggers import ConsoleLogger
from src.data.executors import Executor
from src.data.sources import QueueSource, SerialDataSource, SerialDataSource
from src.data.handlers import Print, ProcessFromUART, ProcessFromUART, ToInt, AddToQueue, Time, Plot
from src.data.executors import HandlersExecutor, Retryer
from src.utils.plot import RefreshingPlot, BatchPlotUpdate
from src.utils.queues import BlockingMultiProcessFetch, NamedQueue, NonBlockingPut


class Experiment(ABC):
    @abstractmethod
    def create_executor(self) -> Executor:
        raise NotImplementedError()


class SerialExperiment(Experiment):
    def __init__(self, queue: NamedQueue) -> None:
        self.__queue = queue

    def create_executor(self) -> Executor:
        logger = ConsoleLogger(prefix="[serial]")
        source = SerialDataSource(
            port='/dev/ttyACM1',
            baudrate=115200,
            sync_byte=b'\n',
            check_byte=b'\xFF',
            # use_parity=True, TODO parity not working
            logger=logger,
            # verbose=True
        )
        handlers = [
            AddToQueue(queue=self.__queue, strategy=NonBlockingPut()),
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor


class ProcessingExperiment(Experiment):
    def __init__(self, source_queue: NamedQueue, csv_queue: NamedQueue, plot_queue: NamedQueue) -> None:
        self.__source_queue = source_queue
        self.__plot_queue = plot_queue
        self.__csv_queue = csv_queue

    def create_executor(self) -> Executor:
        logger = ConsoleLogger(prefix="[processing]")
        source = QueueSource(queue=self.__source_queue, strategy=BlockingMultiProcessFetch())
        handlers = [
            ProcessFromUART(),
            ToInt(),
            Time(logger=logger, timeout=5),
            AddToQueue(queue=self.__plot_queue, strategy=NonBlockingPut()),
            AddToQueue(queue=self.__csv_queue, strategy=NonBlockingPut()),
            # Print(logger=logger)
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor


class CSVExperiment(Experiment):
    def __init__(self, queue: NamedQueue) -> None:
        self.__queue = queue

    def create_executor(self) -> Executor:
        logger = ConsoleLogger(prefix='[csv]')
        source = QueueSource(queue=self.__queue, strategy=BlockingMultiProcessFetch())
        handlers = [
            CSVSaver(file=path.join(Path.cwd(), 'data', str(datetime.now().timestamp()), 'emg.csv'), batch_size=100)
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)

        return executor


class PlottingExperiment(Experiment):
    def __init__(self, plot: RefreshingPlot, queue: NamedQueue) -> None:
        self.__plot_strategy = BatchPlotUpdate(plot=plot, window_size=500, batch_size=500)
        self.__queue = queue

    def create_executor(self) -> Executor:
        logger = ConsoleLogger(prefix='[plot]')
        source = QueueSource(queue=self.__queue, strategy=BlockingMultiProcessFetch())
        handlers = [
            Plot(strategy=self.__plot_strategy),
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)

        return executor


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
                size = queue.queue.qsize()
                total = queue.maxsize
                self.__logger.log(f'{queue.name} : {size}/{total} ({round(size/total*100, 2)}%)')
