from tap import Tap
from src.cli.args import AcquisitionArgs, PredictionArgs, SpeedTestArgs
from scripts import acquisition, speed_test, prediction


class Args(Tap):
    def configure(self) -> None:
        self.add_subparsers(dest='command')
        self.add_subparser('acquisition', AcquisitionArgs, help='Data acquisition for training')
        self.add_subparser('prediction', PredictionArgs, help='Realtime angles prediction')
        self.add_subparser('speed_test', SpeedTestArgs, help='Acquisition speed test')


args = Args().parse_args()

if args.command == 'acquisition':
    acquisition.run(args)
elif args.command == 'prediction':
    prediction.run(args)
elif args.command == 'speed_test':
    speed_test.run(args)
else:
    args.print_help()
