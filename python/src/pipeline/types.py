from dataclasses import replace
from typing import List
import numpy as np
from abc import ABC, abstractmethod


class CharacteristicsExtractor(ABC):
    @abstractmethod
    def extract(self, X: List[int], start_time: float, end_time: float) -> List[float]:
        raise NotImplementedError()


class Model(ABC):
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """"
        Arguments:
            X: List of characteristics per channel (shape: (nb_channels, nb_characteristics))
        """
        raise NotImplementedError()


class Animator(ABC):
    @abstractmethod
    def animate(self, X: np.ndarray) -> None:
        raise NotImplementedError()


# TODO remove once real implementation done
class DumbExtractor(CharacteristicsExtractor):
    def extract(self, X: List[int], start_time: float, end_time: float) -> List[float]:
        return [np.mean(X), np.std(X)]


# TODO remove once real implementation done
class DumbModel(Model):
    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([1.234234, 2.2342342, 3.234234])
