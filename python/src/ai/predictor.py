from scipy.sparse import data
from sklearn.model_selection import train_test_split , cross_val_score ,  RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import scale
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.metrics import r2_score
from sklearn.feature_selection import SelectKBest, RFE, chi2
from utilities import load_csv_data , load_classifier
from transform_unique import WindowsTransformer , FeaturesTransformEMG ,FeaturesTransformAngle
import numpy as np
import pandas as pd
import os
import math

CLASSIFIER_NAME  = ""
classifier = load_classifier(CLASSIFIER_NAME)

def predict(X):

    data_emg = X
    start = data_emg.timestamp.min()
    end =  data_emg.timestamp.max()
    emg_crop = data_emg.loc[(data_emg.timestamp>start) & (data_emg.timestamp<end)]
    emg_crop.reset_index(drop=True, inplace=True)

    WINDOWS_NUMBER_PER_SECOND= 10
    windows_number = math.floor(end-start)*WINDOWS_NUMBER_PER_SECOND

    windows_transform = WindowsTransformer(windows_number)
    emg_transformed = windows_transform.transform(emg_crop.value)
    
    feature_emg_tr = FeaturesTransformEMG()
    dataset = feature_emg_tr.transform(emg_transformed)

    dataset = scale(dataset)
   
    print(f"classifiers {classifier.__class__.__name__}")
    print("-"*30)

    return predict(dataset)