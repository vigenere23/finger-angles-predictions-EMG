from src.cli.args import PredictionArgs
from src.pipeline.experiment.prediction import PredictionExperimentFactory


def run(args: PredictionArgs):
    factory = PredictionExperimentFactory()

    pipeline = factory.create(
        serial_port=args.serial_port,
        model_name=args.model,
        plotting_channels=args.plot,
        predicting_channels=args.predict,
    )

    pipeline.run()
