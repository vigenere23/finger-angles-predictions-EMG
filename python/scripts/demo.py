from src.cli.args import DemoArgs
from src.pipeline.executors.acquisition import AcquisitionExperiment


def run(args: DemoArgs):
    experiment = AcquisitionExperiment(
        serial_port=args.serial_port,
    )

    if args.csv:
        experiment.add_csv_saving()

    for channel in args.plot:
        experiment.add_plotting(channel)
    
    experiment.execute()
