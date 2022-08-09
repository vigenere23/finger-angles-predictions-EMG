from datetime import datetime
from typing import Any, TypeVar

import numpy as np
from modupipe.loader import IdentityLoader, Loader, Sink

from src.animation.base import AnglesAnimator
from src.pipeline.data import ProcessedData, RangeData
from src.utils.loggers import Logger
from src.utils.plot import PlottingStrategy

T = TypeVar("T")


class Plot(Loader[ProcessedData[Any], None]):
    def __init__(self, strategy: PlottingStrategy):
        self.__strategy = strategy

    def load(self, item: ProcessedData[Any]) -> None:
        self.__strategy.update_plot(item.time, [item.original, item.filtered])


class LogRate(IdentityLoader[T]):
    def __init__(self, logger: Logger, timeout: int = 1) -> None:
        self.__start = datetime.now()
        self.__count = 0
        self.__logger = logger
        self.__timeout = timeout

    def load(self, item: T) -> T:
        now = datetime.now()
        self.__count += 1

        if (now - self.__start).seconds >= self.__timeout:
            self.__logger.debug(f"Rate : {round(self.__count/self.__timeout, 2)} / s")
            self.__count = 0
            self.__start = now

        return item


class LogTime(IdentityLoader[T]):
    def __init__(self, logger: Logger):
        self.logger = logger
        self.__start = datetime.now()

    def load(self, item: T) -> T:
        end = datetime.now()
        if (end - self.__start).seconds >= 1:
            self.__start = end
            self.logger.debug(f"Time : {end.timestamp()}")

        return item


class Animate(Sink[RangeData[np.ndarray]]):
    def __init__(self, animator: AnglesAnimator):
        super().__init__()
        self.animator = animator

    def load(self, item: RangeData[np.ndarray]) -> None:
        self.animator.animate(item)
