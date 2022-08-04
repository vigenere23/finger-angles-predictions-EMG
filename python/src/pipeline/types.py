from abc import ABC, abstractmethod

import numpy as np


class CharacteristicsExtractor(ABC):
    @abstractmethod
    def extract(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError()


class PredictionModel(ABC):
    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        raise NotImplementedError()


class Animator(ABC):
    @abstractmethod
    def animate(self, X: np.ndarray) -> None:
        raise NotImplementedError()
