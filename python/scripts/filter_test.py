from numpy import pi, abs
from scipy.signal import freqz
from matplotlib import pyplot as plt

from src.pipeline.filters import NotchFrequency

filter = NotchFrequency(R=0.7, frequency=60, sampling_frequency=2000)
a, b = filter.coefficients()
w, h = freqz(b, a)
plt.plot(w / pi * 2000, abs(h))

plt.show()
