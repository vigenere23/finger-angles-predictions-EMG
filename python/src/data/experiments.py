from abc import ABC, abstractmethod
from multiprocessing import Queue
from os import path
from pathlib import Path
from datetime import datetime
from src.data.savers import CSVSaver
from src.utils.loggers import ConsoleLogger, Logger
from src.data.executors import Executor
from src.data.sources import QueueSource, SerialDataSource
from src.data.handlers import Print, ToInt, AddTimestamp, AddToQueue, Time, Plot
from src.data.executors import HandlersExecutor, Retryer
from src.utils.plot import RefreshingPlot, BatchPlotUpdate
from src.utils.queues import BlockingMultiProcessFetch, BlockingPut, NonBlockingPut


class Experiment(ABC):
    @abstractmethod
    def create_executor(self) -> Executor:
        raise NotImplementedError()

    @abstractmethod
    def get_logger(self) -> Logger:
        raise NotImplementedError()


class SerialExperiment(Experiment):
    def __init__(self, csv_logger: Logger, plot_logger: Logger, csv_queue: Queue, plot_queue: Queue) -> None:
        self.__csv_logger = csv_logger
        self.__plot_logger = plot_logger
        self.__plot_queue = plot_queue
        self.__csv_queue = csv_queue
        self.__logger = ConsoleLogger(prefix="[serial]")

    def create_executor(self) -> Executor:
        source = SerialDataSource(
            port='/dev/ttyACM1',
            baudrate=115200,
            start_byte=b'\x01',
            stop_byte=b'\xfe',
            message_size=4,
            batch_size=10
        )
        handlers = [
            ToInt(),
            AddTimestamp(),
            AddToQueue(queue=self.__plot_queue, strategy=NonBlockingPut(silence=True, logger=self.__plot_logger)),
            AddToQueue(queue=self.__csv_queue, strategy=BlockingPut(silence=True, logger=self.__csv_logger)),
            Time(logger=self.__logger),
            # Print(logger=logger),
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=5)

        return executor

    def get_logger(self) -> Logger:
        return self.__logger


class CSVExperiment(Experiment):
    def __init__(self, queue: Queue) -> None:
        self.__logger = ConsoleLogger(prefix='[csv]')
        self.__queue = queue

    def create_executor(self) -> Executor:
        source = QueueSource(queue=self.__queue, strategy=BlockingMultiProcessFetch())
        handlers = [
            CSVSaver(file=path.join(Path.cwd(), 'data', str(datetime.now().timestamp()), 'emg.csv'), batch_size=500)
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)

        return executor

    def get_logger(self) -> Logger:
        return self.__logger


class PlottingExperiment(Experiment):
    def __init__(self, plot: RefreshingPlot, queue: Queue) -> None:
        self.__logger = ConsoleLogger(prefix='[plot]')
        self.__plot_strategy = BatchPlotUpdate(plot=plot, window_size=20, batch_size=100)
        self.__queue = queue

    def create_executor(self) -> Executor:
        source = QueueSource(queue=self.__queue, strategy=BlockingMultiProcessFetch())
        handlers = [
            Plot(strategy=self.__plot_strategy),
            # Print(logger=self.__logger),
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)

        return executor

    def get_logger(self) -> Logger:
        return self.__logger
