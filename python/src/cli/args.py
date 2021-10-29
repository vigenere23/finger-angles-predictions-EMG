from typing import List
from tap import Tap


class DemoArgs(Tap):
    serial_port: str # write 'fake' for a fake one
    channels: List[int] # channels to use for plotting
    plot: bool = False # plot selected channels
    csv: bool = False # save all data to a CSV


class SpeedTestArgs(Tap):
    serial_port: str # write 'fake' for a fake one
