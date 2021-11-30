import pandas as pd 
import os 
from sklearn.base import BaseEstimator, TransformerMixin
from utilities import *
import numpy as np

class WindowsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self,windows_size,factor):
        self.windows_size = windows_size
        self.factor=factor

    def fit(self, X):
        pass

    def transform(self, X):
        result=[]
        len_data = X.shape[0]
        n_channel = X.shape[1]
        n_window = int(len_data/self.windows_size)
        #each window correspond to an example
        data_windows_ch0 = [X[:,0][w*self.windows_size:w*self.windows_size+self.windows_size] for w in range(n_window)]
        data_windows_ch1 = [X[:,1][w*self.windows_size:w*self.windows_size+self.windows_size] for w in range(n_window)]
        result += [(a, b) for a, b in zip(data_windows_ch0, data_windows_ch1)]
        return result

class FeaturesTransform(BaseEstimator, TransformerMixin):
    def __init__(self,windows_size,factor):
        self.windows_size = windows_size
        self.factor=factor

    def fit(self,X):
        pass
    def transform(self,X):
        dataset =[]
        func_params_list = [getMAV,getVar,getSD,getSSC,getZC,getRMS]
        for exemple in X:
            chann_1= exemple[0]
            chann_2= exemple[1]
            x_1=list()
            for func in func_params_list:
                x_1.append(func(chann_1))
                x_1.append(func(chann_2))
            dataset.append([x_1])
        return dataset

            
        