import pandas as pd 
import os 
from sklearn.base import BaseEstimator, TransformerMixin

class WindowsTransformer(BaseEstimator, TransformerMixin)

    def __init__(self,windows_size,factor):
        self.windows_size = windows_size
        self.factor=factor

    def fit(self, X):
        pass

    def transform(self, X):
        pass


