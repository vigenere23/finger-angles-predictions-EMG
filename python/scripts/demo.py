from src.cli.args import DemoArgs
from src.pipeline.executors.acquisition import AcquisitionExperiment


def run(args: DemoArgs):
    experiment = AcquisitionExperiment(
        serial_port=args.serial_port,
    )

    if args.csv:
        experiment.add_csv_saving()

    if args.plot:
        for channel in args.channels:
            experiment.add_plotting(channel)
    
    experiment.execute()
