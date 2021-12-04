import numpy as np
from abc import ABC, abstractmethod
from src.pipeline.data import RangeData


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
    def animate(self, X: RangeData[np.ndarray]) -> None:
        raise NotImplementedError()


class DumbExtractor(CharacteristicsExtractor):
    def extract(self, X: np.ndarray) -> np.ndarray:
        return np.array([1, 2, 3, 4, 5, 6])


class DumbModel(Model):
    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.array([0, 1, 2])


class DumbAnimator(Animator):
    def animate(self, X: RangeData[np.ndarray]) -> None:
        print(X.data)
