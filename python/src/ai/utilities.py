from sklearn.base import RegressorMixin
from sklearn.metrics import precision_score, recall_score, accuracy_score
from sklearn.model_selection import cross_val_score
import pandas as pd 
import numpy as np
import os
from pathlib import Path
import pickle

DATA_FOLDER = os.path.join(Path.cwd(), 'data')
MODELS_FOLDER = os.path.join(Path.cwd(), 'src', 'ai', 'models')

def cross_validation(model, X, y):
    scores = cross_val_score(model, X, y, cv=5)
    print("\nÉvaluation par validation croisée (en entraînement) : ")
    print("   Exactitude (accuracy) sur chaque partition", scores)
    print("   Exactitude moyenne: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))


def hold_out_evaluation(model, X, y_true):
    y_pred = model.predict(X)
    print("\nÉvaluation sur les données de tests")
    print("   Accuracy = ", accuracy_score(y_true, y_pred))
    print("   Macro rappel (recall) = ", recall_score(y_true, y_pred, average='macro'))
    print("   Macro précision = ", precision_score(y_true, y_pred, average='macro'))
    print("   Micro rappel (recall) = ", recall_score(y_true, y_pred, average='micro'))
    print("   Micro précision = ", precision_score(y_true, y_pred, average='micro'))

def load_csv_data(file_name, delimiter= ";") -> pd.DataFrame:
    file_path  = os.path.join(DATA_FOLDER, file_name)
    return pd.read_csv(file_path, delimiter=delimiter)

def load_model(model_name) -> RegressorMixin:
    file_path = os.path.join(MODELS_FOLDER, f'model_{model_name}')
    
    with open(file_path, 'rb') as file:
        return pickle.load(file)

def save_model(model, model_name: str):
    file_path = os.path.join(MODELS_FOLDER, f'model_{model_name}')
    
    with open(file_path, 'wb') as file:
        pickle.dump(model, file)

def getMAV(x):
    '''
    Computes the Mean Absolute Value (MAV)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Mean Absolute Value as [float]
    '''
    MAV = np.mean(np.abs(x))
    return MAV

def getRMS(x):
    '''
    Computes the Root Mean Square value (RMS)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Root Mean Square value as [float]
    '''
    RMS = np.sqrt(np.mean(x**2))
    return RMS

def getVar(x):
    '''
    Computes the Variance of EMG (Var)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Variance of EMG as [float]
    '''
    N = np.size(x)
    Var = (1/(N-1))*np.sum(x**2)
    return Var

def getSD(x):
    '''
    Computes the Standard Deviation (SD)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Standard Deviation as [float]
    '''
    N = np.size(x)
    xx = np.mean(x)
    SD = np.sqrt(1/(N-1)*np.sum((x-xx)**2))
    return SD

def getZC(x, threshold=0):
    '''
    Computes the Zero Crossing value (ZC)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Zero Crossing value as [float]
    '''
    N = np.size(x)
    ZC=0
    for i in range(N-1):
        if (x[i]*x[i+1] < 0) and (np.abs(x[i]-x[i+1]) >= threshold):
            ZC += 1
    return ZC

def getSSC(x, threshold=0):
    '''
    Computes the Slope Sign Change value (SSC)
    :param x: EMG signal vector as [1-D numpy array]
    :return: Slope Sign Change value as [float]
    '''
    N = np.size(x)
    SSC = 0
    for i in range(1, N-1):
        if (((x[i] > x[i-1]) and (x[i] > x[i+1])) or ((x[i] < x[i-1]) and (x[i] < x[i+1]))) and ((np.abs(x[i]-x[i+1]) >= threshold) or (np.abs(x[i]-x[i-1]) >= threshold)):
            SSC += 1
    return SSC