from datetime import datetime
from typing import Any

from modupipe.sink import Sink

from src.pipeline.data import ProcessedData
from src.utils.loggers import Logger
from src.utils.plot import PlottingStrategy


class Plot(Sink[ProcessedData[Any]]):
    def __init__(self, strategy: PlottingStrategy):
        self.__strategy = strategy

    def receive(self, item: ProcessedData[Any]) -> None:
        self.__strategy.update_plot(item.time, [item.original, item.filtered])


class LogRate(Sink[Any]):
    def __init__(self, logger: Logger, timeout: int = 1) -> None:
        self.__start = datetime.now()
        self.__count = 0
        self.__logger = logger
        self.__timeout = timeout

    def receive(self, _: Any) -> None:
        now = datetime.now()
        self.__count += 1

        if (now - self.__start).seconds >= self.__timeout:
            self.__logger.log(f"Rate : {round(self.__count/self.__timeout, 2)} / s")
            self.__count = 0
            self.__start = now


class LogTime(Sink[Any]):
    def __init__(self, logger: Logger):
        self.logger = logger
        self.__start = datetime.now()

    def receive(self, _: Any) -> None:
        end = datetime.now()
        if (end - self.__start).seconds >= 1:
            self.__start = end
            self.logger.log(f"Time : {end.timestamp()}")
