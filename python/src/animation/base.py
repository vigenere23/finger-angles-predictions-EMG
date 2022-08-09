from abc import ABC, abstractmethod

import numpy as np

from src.pipeline.data import RangeData
from src.utils.loggers import Logger


class AnglesAnimator(ABC):
    @abstractmethod
    def animate(self, item: RangeData[np.ndarray]) -> None:
        raise NotImplementedError()


class ConsoleAnglesAnimator(AnglesAnimator):
    def __init__(self, logger: Logger) -> None:
        self.logger = logger

    def animate(self, item: RangeData[np.ndarray]) -> None:
        self.logger.info(f"Angles: {item.value}")
