from src.cli.args import PredictionArgs
from src.pipeline.executors.prediction_experiment import PredictionExperimentBuilder


def run(args: PredictionArgs):
    builder = PredictionExperimentBuilder()

    for channel in args.plot:
        builder.add_plotting_for(channel)

    for channel in args.predict:
        builder.add_prediction_for(channel)

    builder.set_serial_port(serial_port=args.serial_port)
    builder.set_model_name(args.model)

    if args.animate:
        builder.add_animation()

    experiment = builder.build()
    experiment.execute()
