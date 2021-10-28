from typing import List
from tap import Tap


class DemoArgs(Tap):
    serial_port: str
    channels: List[int]
    plot: bool = False
    csv: bool = False


class SpeedTestArgs(Tap):
    serial_port: str
