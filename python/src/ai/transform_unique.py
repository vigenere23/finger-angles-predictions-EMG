import numpy as np
from src.ai.utilities import *
from src.pipeline.types import CharacteristicsExtractor

class WindowsTransformer():
    def __init__(self, windows_number):
        self.number_of_windows = windows_number

    def transform(self, X: np.ndarray):
        len_data = X.shape[0]
        windows_size = int(len_data/self.number_of_windows)

        windowed_data = [X[window_number*windows_size:(window_number+1)*windows_size] for window_number in range(self.number_of_windows)]

        return np.array(windowed_data)

class FeaturesTransformEMG(CharacteristicsExtractor):
    def __init__(self) -> None:
        self.__extractors = [getMAV, getVar, getSD, getSSC, getZC, getRMS]

    def extract(self, X: np.ndarray) -> np.ndarray:
        return self.transform(X)

    def transform(self, X: np.ndarray):
        dataset = []
        
        for example in X:
            characteristics = [extractor(example) for extractor in self.__extractors]
            dataset.append(characteristics)

        return np.array(dataset)

class FeaturesTransformAngle():
    def transform(self, X: np.ndarray): 
        return X.mean(axis=1)
