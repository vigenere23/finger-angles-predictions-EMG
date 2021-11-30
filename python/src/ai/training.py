from sklearn.model_selection import train_test_split , cross_val_score ,  RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler , normalize
from sklearn.linear_model import LinearRegression, ElasticNet

from python.src.ai.utilities import load_csv_data
from transform import WindowsTransformer , FeaturesTransform
import numpy as np


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
    

def make_dataset(X,y):
    transformer = WindowsTransformer(windows_size=3,factor=1)
    features_transformer = FeaturesTransform(windows_size=3,factor=1)
    print(f"original data {fake_data}")
    windowed_data = transformer.transform(X)
    features_data =  features_transformer.transform(windowed_data)
    print(np.array(features_data)[:,0])
    pass


if __name__=="__main__":
    #load_data()
    data1=load_csv_data("dummy.csv")
    data2=load_csv_data("dummy_2.csv")
    #extract features 
    dataset =make_dataset(data1,data2)
    X_train, X_test, y_train, y_test = train_test_split(dataset.X, dataset.y, test_size=0.33, random_state=42)
    clf_lin_reg = LinearRegression() #add parametrers
    clf_lin_elastic = ElasticNet()
    classfiers = [clf_lin_elastic,clf_lin_reg]

    for clf in classfiers: 
        print(f"classifiers {clf.__class__.__name__}")
        print("-"*30)
        train_score = train_k_fold(clf)
        print(f"Training score {train_score}")




