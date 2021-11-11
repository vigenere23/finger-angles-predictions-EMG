from tap import Tap
from src.cli.args import DemoArgs, SpeedTestArgs
from scripts import demo, speed_test


class Args(Tap):
    def configure(self) -> None:
        self.add_subparsers(dest='command')
        self.add_subparser('demo', DemoArgs, help='Acquisition demo to test modules')
        self.add_subparser('speed_test', SpeedTestArgs, help='Acquisition speed test')


args = Args().parse_args()

if args.command == 'demo':
    demo.run(args)
elif args.command == 'speed_test':
    speed_test.run(args)
else:
    args.print_help()
