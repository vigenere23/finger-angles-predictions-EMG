from sklearn.model_selection import train_test_split , cross_val_score ,  RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import scale
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.metrics import r2_score
from sklearn.feature_selection import SelectKBest, RFE, chi2
from utilities import load_csv_data
from transform_unique import WindowsTransformer , FeaturesTransformEMG ,FeaturesTransformAngle
import numpy as np
import pandas as pd
import os
import math


def train_k_fold(model,X,y,factor=0.7):
    avgScoreTemp = []

    kFold_rep = 3
    kFold_splits = 3
    kFold = RepeatedKFold(n_splits=kFold_splits, n_repeats=kFold_rep)

    for i in range(kFold_rep):
        for i_Train, i_Test in kFold.split(X):
            clf = model
            X_train, X_test = [X[j] for j in i_Train], [X[k] for k in i_Test]
            y_train, y_test = [y[l] for l in i_Train], [y[m] for m in i_Test]

            clf.fit(X_train, y_train)
            currentScore = clf.score(X_test, y_test)

            avgScoreTemp += [currentScore]

    avgScore = sum(avgScoreTemp)/len(avgScoreTemp)
    print('Mean score with k-fold validation: {}'.format(avgScore))
    

    

def predict_regression(X,y):
    pass


if __name__=="__main__":
    #load_data()
    dirname = r"acq-3"
    file_name_emg = "emg-0.csv"
    file_name_hand_angle= "Hand_angles_record_3.csv"
    file_path_emg = os.path.join(dirname,file_name_emg)
    file_path_angle = os.path.join(".",file_name_hand_angle)
    data_emg  = load_csv_data(file_name=file_path_emg)
    data_hand_angle  = load_csv_data(file_name=file_name_hand_angle,sep=",",delimiter=",")

    #time for training data slice
    start = data_hand_angle.timestamp.min()
    end =  data_hand_angle.timestamp.max()
    emg_crop = data_emg.loc[(data_emg.timestamp>start) & (data_emg.timestamp<end)]
    angle_crop=data_hand_angle[(data_hand_angle.timestamp>start) & (data_hand_angle.timestamp<end)]
    emg_crop.reset_index(drop=True, inplace=True)
    angle_crop.reset_index(drop=True, inplace=True)

    WINDOWS_NUMBER_PER_SECOND= 10
    windows_number = math.floor(end-start)*WINDOWS_NUMBER_PER_SECOND

    windows_transform = WindowsTransformer(windows_number)
    angle_transformed = windows_transform.transform(angle_crop.drop(columns=["timestamp"]))
    emg_transformed = windows_transform.transform(emg_crop.value)
    feature_angle_tr = FeaturesTransformAngle()
    feature_emg_tr = FeaturesTransformEMG()
    target = feature_angle_tr.transform(angle_transformed)
    trainset = feature_emg_tr.transform(emg_transformed)

    trainset = scale(trainset)
    X_train, X_test, y_train, y_test = train_test_split(trainset,target, test_size=0.20, random_state=42)
    clf_lin_reg = LinearRegression() #add parametrers
    clf_lin_elastic = ElasticNet()
    classfiers = [clf_lin_elastic,clf_lin_reg]

for clf in classfiers: 
    #X_test_transform=selector.transform(X_test)
    print(f"classifiers {clf.__class__.__name__}")
    print("-"*30)
    clf.fit(X_train,y_train)
    train_score = r2_score(y_train,clf.predict(X_train))
    print(f"Training score {train_score}")
    test_score  = r2_score(y_test,clf.predict(X_test))




