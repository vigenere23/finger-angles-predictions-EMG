from typing import List
from tap import Tap


class AcquisitionArgs(Tap):
    serial_port: str # use 'rand' for random generation, or 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>' for specific frequencies generation
    csv: List[int] = [] # channels to use for CSV
    plot: List[int] = [] # channels to use for plotting

    def configure(self) -> None:
        self.add_argument('--plot', metavar='CHANNEL')
        self.add_argument('--csv', metavar='CHANNEL')


class PredictionArgs(Tap):
    serial_port: str # use 'rand' for random generation, or 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>' for specific frequencies generation
    predict: List[int] = [] # channels to use for prediction
    plot: List[int] = [] # channels to use for plotting
    animate: bool = False # show animation of predicted angles. If False, will print to console.

    def configure(self) -> None:
        self.add_argument('--predict', metavar='CHANNEL', required=True)
        self.add_argument('--plot', metavar='CHANNEL')


class SpeedTestArgs(Tap):
    serial_port: str # use 'rand' for random generation, or 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>' for specific frequencies generation
