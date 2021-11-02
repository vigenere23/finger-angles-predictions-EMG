from typing import List
from tap import Tap


class DemoArgs(Tap):
    serial_port: str # write 'fake' for a fake one
    csv: bool = False # save all data to a CSV
    plot: List[int] = [] # channels to use for plotting

    def configure(self) -> None:
        self.add_argument('--plot', metavar='CHANNEL')


class SpeedTestArgs(Tap):
    serial_port: str # write 'fake' for a fake one
