from modupipe.runnable import Runnable

from src.pipeline2.sources import SerialSourceFactory


class AcquisitionExperimentBuilder:
    def __init__(self, serial_port: str) -> None:
        self.serial_source = SerialSourceFactory().create(port=serial_port)

    def add_plotting_for(self, channel: int) -> None:
        pass

    def add_csv_for(self, channel: int) -> None:
        pass

    def build(self) -> Runnable:
        pass
