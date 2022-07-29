import math

from sklearn.preprocessing import scale
from utilities import load_model

from src.ai.transform_unique import FeaturesTransformEMG, WindowsTransformer

CLASSIFIER_NAME = ""
classifier = load_model(CLASSIFIER_NAME)


def predict(X):

    data_emg = X
    start = data_emg.timestamp.min()
    end = data_emg.timestamp.max()
    emg_crop = data_emg.loc[(data_emg.timestamp > start) & (data_emg.timestamp < end)]
    emg_crop.reset_index(drop=True, inplace=True)

    WINDOWS_NUMBER_PER_SECOND = 10
    windows_number = math.floor(end - start) * WINDOWS_NUMBER_PER_SECOND

    windows_transform = WindowsTransformer(windows_number)
    emg_transformed = windows_transform.transform(emg_crop.value)

    feature_emg_tr = FeaturesTransformEMG()
    dataset = feature_emg_tr.transform(emg_transformed)

    dataset = scale(dataset)

    print(f"classifiers {classifier.__class__.__name__}")
    print("-" * 30)

    return classifier.predict(dataset)
