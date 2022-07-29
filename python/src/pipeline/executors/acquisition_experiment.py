import os
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Queue
from pathlib import Path
from typing import Dict, List

from src.pipeline.executors.base import Executor, ExecutorFactory, ProcessesExecutor
from src.pipeline.executors.csv import CSVExecutorFactory
from src.pipeline.executors.plotting import PlottingExecutorFactory
from src.pipeline.executors.processing import ProcessingExecutorFactory
from src.pipeline.executors.queues import QueuesExecutorFactory
from src.pipeline.executors.serial import SerialExecutorFactory
from src.pipeline.filters import NotchDC, NotchFrequencyOnline
from src.pipeline.handlers import (
    AddToQueue,
    ChannelSelection,
    ConditionalHandler,
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
    csv: bool = False


class AcquisitionExperiment(Executor):
    def __init__(self, serial_port: str, configs: List[ChannelConfig]):
        executor_factories: Dict[str, ExecutorFactory] = {}
        queues = []
        processing_outputs = []

        base_csv_path = os.path.join(
            Path.cwd(), "data", f"acq-{datetime.now().timestamp()}"
        )

        for config in configs:
            handlers = [
                NotchDC(R=0.99),
                NotchFrequencyOnline(frequency=60, sampling_frequency=2500),
            ]

            if config.plot:
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

            if config.csv:
                queue = NamedQueue(name=f"csv-{config.channel}", queue=Queue())
                handlers.append(AddToQueue(queue=queue, strategy=NonBlockingPut()))

                path = os.path.join(base_csv_path, f"emg-{config.channel}.csv")
                csv = CSVExecutorFactory(
                    source=QueueSource(queue=queue, strategy=BlockingFetch()), path=path
                )

                executor_factories[f"CSV-{config.channel}"] = csv
                queues.append(queue)

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

    def execute(self):
        self.__executor.execute()


class AcquisitionExperimentBuilder:
    def __init__(self):
        self.__serial_port = "fake"
        self.__channel_configs: Dict[int, ChannelConfig] = {}

    def __get_or_create_config(self, channel: int) -> ChannelConfig:
        if self.__channel_configs.get(channel) is None:
            self.__channel_configs[channel] = ChannelConfig(channel=channel)

        return self.__channel_configs[channel]

    def __save_config(self, config: ChannelConfig):
        self.__channel_configs[config.channel] = config

    def set_serial_port(self, serial_port: str):
        self.__serial_port = serial_port

    def add_plotting_for(self, channel: int):
        config = self.__get_or_create_config(channel)
        config.plot = True
        self.__save_config(config)

    def add_csv_for(self, channel: int):
        config = self.__get_or_create_config(channel)
        config.csv = True
        self.__save_config(config)

    def build(self) -> AcquisitionExperiment:
        return AcquisitionExperiment(
            serial_port=self.__serial_port, configs=self.__channel_configs.values()
        )
