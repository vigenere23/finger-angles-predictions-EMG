from tap import Tap
from enum import Enum
from scripts import acquisition, speed_test, prediction, detection
from src.cli.args import AcquisitionArgs, DetectionArgs, PredictionArgs, SpeedTestArgs


class Commands(Enum):
    ACQUISITION = 'acquisition'
    PREDICTION = 'prediction'
    DETECTION = 'detection'
    SPEED_TEST = 'speed_test'


class Args(Tap):
    def configure(self) -> None:
        self.add_subparsers(dest='command')
        self.add_subparser(Commands.ACQUISITION.value, AcquisitionArgs, help='Data acquisition for training')
        self.add_subparser(Commands.PREDICTION.value, PredictionArgs, help='Realtime angles prediction')
        self.add_subparser(Commands.DETECTION.value, DetectionArgs, help='Detect finger angles using camera')
        self.add_subparser(Commands.SPEED_TEST.value, SpeedTestArgs, help='Acquisition speed test')


args = Args().parse_args()

if args.command == Commands.ACQUISITION.value:
    acquisition.run(args)
elif args.command == Commands.PREDICTION.value:
    prediction.run(args)
elif args.command == Commands.DETECTION.value:
    detection.run(args)
elif args.command == Commands.SPEED_TEST.value:
    speed_test.run(args)
else:
    args.print_help()
