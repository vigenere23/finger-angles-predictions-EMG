from typing import List
from tap import Tap


class DemoArgs(Tap):
    serial_port: str # write 'fake' for a fake one
    csv: bool = False # save all data to a CSV
    plot: bool = False # plot selected channels
    plot_channels: List[int] = [] # channels to use for plotting


class SpeedTestArgs(Tap):
    serial_port: str # write 'fake' for a fake one
