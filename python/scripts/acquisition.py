from src.cli.args import AcquisitionArgs
from src.pipeline2.experiment.acquisition import AcquisitionExperimentFactory


def run(args: AcquisitionArgs):
    factory = AcquisitionExperimentFactory()

    pipeline = factory.create(
        serial_port=args.serial_port,
        plotting_channels=args.plot,
        saving_channels=args.csv,
    )

    pipeline.run()
