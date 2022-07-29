from dataclasses import dataclass
from multiprocessing import Queue
from typing import Dict, List, Optional

from src.ai.transform_unique import FeaturesTransformEMG
from src.ai.utilities import load_model
from src.pipeline.executors.base import Executor, ExecutorFactory, ProcessesExecutor
from src.pipeline.executors.plotting import PlottingExecutorFactory
from src.pipeline.executors.prediction import PredictionExecutorFactory
from src.pipeline.executors.processing import ProcessingExecutorFactory
from src.pipeline.executors.queues import QueuesExecutorFactory
from src.pipeline.executors.serial import SerialExecutorFactory
from src.pipeline.filters import NotchDC, NotchFrequencyOnline
from src.pipeline.handlers import (
    AddToQueue,
    ChannelSelection,
    ConditionalHandler,
    DataHandler,
    HandlersList,
)
from src.pipeline.processes import ExecutorProcess, SleepingExecutorProcess
from src.pipeline.sources import QueueSource
from src.utils.plot import RefreshingPlot
from src.utils.queues import BlockingFetch, NamedQueue, NonBlockingPut


@dataclass
class ChannelConfig:
    channel: int
    plot: bool = False
    predict: bool = False


class PredictionExperiment(Executor):
    def __init__(
        self,
        serial_port: str,
        animate: bool,
        model_name: str,
        configs: List[ChannelConfig],
    ):
        executor_factories: Dict[str, ExecutorFactory] = {}
        queues = []
        processing_outputs = []
        prediction_queue = self.__add_global_prediction(
            model_name, configs, queues, executor_factories, animate=animate
        )

        for config in configs:
            handlers = [
                NotchDC(R=0.99),
                NotchFrequencyOnline(frequency=60, sampling_frequency=2500),
            ]

            if config.plot:
                self.__add_plotting(config, handlers, queues, executor_factories)

            if config.predict:
                self.__add_prediction(prediction_queue, handlers)

            handlers_list = HandlersList(handlers)

            processing_outputs.append(
                ConditionalHandler(
                    condition=ChannelSelection(config.channel), child=handlers_list
                )
            )

        processing_queue = NamedQueue(name="processing", queue=Queue())
        processing = ProcessingExecutorFactory(
            source=QueueSource(queue=processing_queue, strategy=BlockingFetch()),
            output_handler=HandlersList(processing_outputs),
        )

        queues.append(processing_queue)
        executor_factories["Processing"] = processing

        serial = SerialExecutorFactory(
            port=serial_port,
            output_handler=AddToQueue(
                queue=processing_queue, strategy=NonBlockingPut()
            ),
        )
        executor_factories["Serial"] = serial

        processes = []
        for process_name, executor_factory in executor_factories.items():
            processes.append(
                ExecutorProcess(name=process_name, executor=executor_factory.create())
            )
        processes.append(
            SleepingExecutorProcess(
                name="Queues",
                executor=QueuesExecutorFactory(queues=queues).create(),
                sleep_time=5,
            )
        )

        self.__executor = ProcessesExecutor(processes=processes)

    def __add_plotting(
        self,
        config: ChannelConfig,
        handlers: List[DataHandler],
        queues: List[NamedQueue],
        executor_factories: Dict[str, ExecutorFactory],
    ):
        queue = NamedQueue(name=f"plot-{config.channel}", queue=Queue())
        handlers.append(AddToQueue(queue=queue, strategy=NonBlockingPut()))

        plot = RefreshingPlot(
            series=["original", "filtered"],
            title=f"Data from channel {config.channel}",
            x_label="time",
            y_label="value",
        )
        plotting = PlottingExecutorFactory(
            plot=plot,
            source=QueueSource(queue=queue, strategy=BlockingFetch()),
            n_ys=2,
            window_size=2000,
        )

        executor_factories[f"Plot-{config.channel}"] = plotting
        queues.append(queue)

    def __add_prediction(self, queue: NamedQueue, handlers: List[DataHandler]):
        handlers.append(AddToQueue(queue=queue, strategy=NonBlockingPut()))

    def __add_global_prediction(
        self,
        model_name: str,
        configs: List[ChannelConfig],
        queues: List[NamedQueue],
        executor_factories: Dict[str, ExecutorFactory],
        animate: bool = False,
    ) -> Optional[NamedQueue]:
        channels = list(
            map(
                lambda config: config.channel,
                filter(lambda config: config.predict, configs),
            )
        )

        if channels == []:
            return None

        queue = NamedQueue(name="predictions", queue=Queue())

        prediction = PredictionExecutorFactory(
            source=QueueSource(queue=queue, strategy=BlockingFetch()),
            channels=channels,
            model=load_model(model_name=model_name),
            extractor=FeaturesTransformEMG(),
            animate=animate,
        )

        executor_factories["Prediction"] = prediction
        queues.append(queue)

        return queue

    def execute(self):
        self.__executor.execute()


class PredictionExperimentBuilder:
    def __init__(self):
        self.__serial_port = "fake"
        self.__animate = False
        self.__model_name = ""
        self.__channel_configs: Dict[int, ChannelConfig] = {}

    def __get_or_create_config(self, channel: int) -> ChannelConfig:
        if self.__channel_configs.get(channel) is None:
            self.__channel_configs[channel] = ChannelConfig(channel=channel)

        return self.__channel_configs[channel]

    def __save_config(self, config: ChannelConfig):
        self.__channel_configs[config.channel] = config

    def set_serial_port(self, serial_port: str):
        self.__serial_port = serial_port

    def set_model_name(self, model_name: str):
        self.__model_name = model_name

    def add_plotting_for(self, channel: int):
        config = self.__get_or_create_config(channel)
        config.plot = True
        self.__save_config(config)

    def add_prediction_for(self, channel: int):
        config = self.__get_or_create_config(channel)
        config.predict = True
        self.__save_config(config)

    def add_animation(self):
        self.__animate = True

    def build(self) -> PredictionExperiment:
        return PredictionExperiment(
            serial_port=self.__serial_port,
            animate=self.__animate,
            model_name=self.__model_name,
            configs=self.__channel_configs.values(),
        )
