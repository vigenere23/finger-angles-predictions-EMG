from sklearn.metrics import precision_score, recall_score, accuracy_score,confusion_matrix
from sklearn.model_selection import cross_val_score
import pandas as pd 

DATA_FOLDER = "data"

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

def load_csv_data(file_name)
    dirname = DATA_FOLDER
    file_path  = os.path.join(dirname,file_name)
    return pd.read_csv(file_path)