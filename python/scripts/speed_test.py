from src.cli.args import SpeedTestArgs
from src.pipeline2.experiment.speed_test import SpeedTestExperimentFactory


def run(args: SpeedTestArgs):
    pipeline = SpeedTestExperimentFactory().create(serial_port=args.serial_port)
    pipeline.run()
