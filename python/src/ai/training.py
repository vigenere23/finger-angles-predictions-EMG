from sklearn.model_selection import train_test_split, RepeatedKFold
from sklearn.preprocessing import scale
from sklearn.linear_model import LinearRegression, ElasticNet
from sklearn.metrics import r2_score
import os
import math
from src.ai.utilities import load_csv_data, save_model
from src.ai.transform_unique import WindowsTransformer, FeaturesTransformEMG, FeaturesTransformAngle


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


def main():
    file_path_angles = os.path.join('acq-3', 'angles.csv')
    file_path_emg = os.path.join('acq-3', 'emg-0.csv')
    data_emg = load_csv_data(file_name=file_path_emg)
    data_hand_angle = load_csv_data(file_name=file_path_angles, delimiter=",")

    #time for training data slice
    start = data_hand_angle.timestamp.min()
    end = data_hand_angle.timestamp.max()
    emg_crop = data_emg.loc[(data_emg.timestamp>start) & (data_emg.timestamp<end)]
    
    emg_data = emg_crop.reset_index(drop=True).drop(columns=["timestamp"]).values
    angles_data = data_hand_angle.reset_index(drop=True).drop(columns=["timestamp"]).values

    WINDOWS_NUMBER_PER_SECOND = 1
    windows_number = math.floor(end-start) * WINDOWS_NUMBER_PER_SECOND
    windows_transformer = WindowsTransformer(windows_number)
    
    windowed_angles = windows_transformer.transform(angles_data)
    windowed_emg = windows_transformer.transform(emg_data)

    feature_angle_tr = FeaturesTransformAngle()
    feature_emg_tr = FeaturesTransformEMG()
    
    target = feature_angle_tr.transform(windowed_angles)
    trainset = feature_emg_tr.transform(windowed_emg)

    # trainset = scale(trainset)
    X_train, X_test, y_train, y_test = train_test_split(trainset, target, test_size=0.10, random_state=42)
    linear_model = LinearRegression() #add parametrers
    elastic_net_model = ElasticNet()
    # classfiers = [elastic_net_model, linear_model]
    classfiers = [linear_model]

    for model in classfiers: 
        #X_test_transform=selector.transform(X_test)
        model_name = model.__class__.__name__
        print(f"\nClassifier : {model_name}")
        print("-"*30)
        model.fit(X_train,y_train)
        train_score = r2_score(y_train, model.predict(X_train))
        print(f"Train score {train_score}")
        test_score = r2_score(y_test, model.predict(X_test))
        print(f"Test score {test_score}")
        save_model(model=model, model_name=model_name)


if __name__=="__main__":
    main()
