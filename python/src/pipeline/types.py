from typing import List
import numpy as np
from abc import ABC, abstractmethod


class CharacteristicsExtractor(ABC):
    @abstractmethod
    def extract(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError()


class Model(ABC):
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError()


class Animator(ABC):
    @abstractmethod
    def animate(self, X: np.ndarray) -> None:
        raise NotImplementedError()
