from typing import List
from tap import Tap


class DemoArgs(Tap):
    serial_port: str # use 'rand' for random generation, or 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>' for specific frequencies generation
    csv: List[int] = [] # channels to use for CSV
    plot: List[int] = [] # channels to use for plotting

    def configure(self) -> None:
        self.add_argument('--plot', metavar='CHANNEL')
        self.add_argument('--csv', metavar='CHANNEL')


class SpeedTestArgs(Tap):
    serial_port: str # use 'rand' for random generation, or 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>' for specific frequencies generation
