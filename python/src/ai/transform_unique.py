import pandas as pd 
import os 
from sklearn.base import BaseEstimator, TransformerMixin
from utilities import *
import numpy as np

class WindowsTransformer(BaseEstimator, TransformerMixin):
    def __init__(self,windows_number):
        self.windows_number = windows_number
        
    def fit(self, X):
        pass

    def transform(self, X,**kwargs):
    
        result=[]
        len_data = X.shape[0]
        
        windows_size = int(len_data/self.windows_number)
        #each window correspond to an example
        data_windows_ch0 = [X[w*windows_size:w*windows_size+windows_size] for w in range(self.windows_number)]

        result = data_windows_ch0
        return result

class FeaturesTransformEMG(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self,X):
        pass
    def transform(self,X):
        dataset =[]
        func_params_list = [getMAV,getVar,getSD,getSSC,getZC,getRMS]
        for exemple in X:
            chann_1= np.array(exemple)  
            x_1=list()
            for func in func_params_list:
                x_1.append(func(chann_1))
            dataset.append(x_1)
        return dataset

class FeaturesTransformAngle(BaseEstimator, TransformerMixin):
    def __init__(self):
        pass

    def fit(self,X):
        pass
    def transform(self,X): 
        return [angle.mean().tolist() for angle in X]