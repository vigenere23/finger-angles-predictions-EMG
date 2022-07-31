from src.cli.args import AcquisitionArgs
from src.pipeline.executors.acquisition_experiment import AcquisitionExperimentBuilder


def run(args: AcquisitionArgs):
    builder = AcquisitionExperimentBuilder()

    for channel in args.plot:
        builder.add_plotting_for(channel)

    for channel in args.csv:
        builder.add_csv_for(channel)

    builder.set_serial_port(serial_port=args.serial_port)

    experiment = builder.build()
    experiment.execute()
