from modupipe.runnable import FullPipeline, NamedRunnable, Retry, Runnable

from src.pipeline2.loaders import LogRate
from src.pipeline2.mappers import ProcessFromSerial, ToInt
from src.pipeline2.serial import SerialSourceFactory
from src.utils.loggers import ConsoleLogger


class SpeedTestExperimentFactory:
    def create(self, serial_port: str) -> Runnable:
        logger = ConsoleLogger(name="speed-test")
        source = SerialSourceFactory().create(port=serial_port)
        mappers = ProcessFromSerial() + ToInt() + LogRate(logger)

        pipeline = NamedRunnable(
            "Speed test", Retry(FullPipeline(source + mappers), nb_times=5)
        )

        return pipeline
