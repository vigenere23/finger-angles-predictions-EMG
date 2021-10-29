from src.cli.args import SpeedTestArgs
from src.pipeline.executors.speed_test import SpeedTest


def run(args: SpeedTestArgs):
    experiment = SpeedTest(serial_port=args.serial_port)
    experiment.execute()
