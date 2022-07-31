import numpy as np

from src.ai.transform_unique import FeaturesTransform, WindowsTransformer

fake_data = np.random.randint(5, size=(8, 2))
transformer = WindowsTransformer(windows_size=3, factor=1)
features_transformer = FeaturesTransform(windows_size=3, factor=1)
print(f"original data {fake_data}")
windowed_data = transformer.transform(fake_data)
features_data = features_transformer.transform(windowed_data)
print(np.array(features_data)[:, 0])
