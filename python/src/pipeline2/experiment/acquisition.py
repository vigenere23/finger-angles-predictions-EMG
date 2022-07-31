import multiprocessing
import os
import pathlib
from datetime import datetime
from typing import List

from modupipe.queue import GetBlocking, PutNonBlocking, Queue
from modupipe.runnable import MultiProcess, Pipeline, Retry, Runnable
from modupipe.sink import ConditionalSink, QueueSink, Sink, SinkList
from modupipe.source import QueueSource

from src.pipeline2.conditions import ChannelSelection
from src.pipeline2.csv import CSVWriter, WithoutChannel
from src.pipeline2.mappers import Log, ProcessFromSerial, TimeChecker, ToInt
from src.pipeline2.serial import SerialSourceFactory
from src.pipeline.data import ProcessedData, SerialData
from src.utils.loggers import ConsoleLogger


class SourcePipelineFactory:
    def create(self, serial_port: str, out_queue: Queue[SerialData[bytes]]) -> Runnable:
        source = SerialSourceFactory().create(port=serial_port)
        sink = QueueSink(out_queue, strategy=PutNonBlocking())

        pipeline = Pipeline(source, sink)
        return Retry(pipeline, nb_times=10)


class ProcessingPipelineFactory:
    def create(
        self,
        in_queue: Queue[SerialData[bytes]],
        sink: Sink[ProcessedData[int]],
    ) -> Runnable:
        logger = ConsoleLogger(prefix="[processing]")

        source = QueueSource(in_queue, strategy=GetBlocking())
        mapper = ProcessFromSerial() + ToInt() + Log(logger) + TimeChecker()

        pipeline = Pipeline(source + mapper, sink)
        return Retry(pipeline, nb_times=1)


class SavingPipelineFactory:
    def create(
        self, source_queue: Queue[ProcessedData[int]], filename: str
    ) -> Runnable:
        source = QueueSource(source_queue)
        sink = CSVWriter[ProcessedData[int]](
            file=filename, batch_size=100, strategy=WithoutChannel()
        )

        return Pipeline(source, sink)


class AcquisitionExperimentFactory:
    def create(
        self,
        serial_port: str,
        plotting_channels: List[int] = [],
        saving_channels: List[int] = [],
    ) -> Runnable:
        experiment_path = os.path.join(
            pathlib.Path.cwd(), "data", f"acq-{datetime.now().timestamp()}"
        )
        pipelines: List[Runnable] = []

        source_out_queue = Queue[SerialData[bytes]](
            multiprocessing.Queue()
        )  # TODO maxsize?

        source_pipeline = SourcePipelineFactory().create(
            serial_port=serial_port, out_queue=source_out_queue
        )
        pipelines.append(source_pipeline)

        processing_sinks: List[Sink[ProcessedData[int]]] = []
        used_channels = set(plotting_channels + saving_channels)

        for channel in used_channels:
            channel_sinks: List[Sink[ProcessedData[int]]] = []

            if channel in plotting_channels:
                queue = Queue(multiprocessing.Queue())
                channel_sinks.append(QueueSink(queue, strategy=PutNonBlocking()))
                # TODO create pipeline using queue

            if channel in saving_channels:
                queue = Queue(multiprocessing.Queue())
                channel_sinks.append(QueueSink(queue, strategy=PutNonBlocking()))
                filename = os.path.join(experiment_path, f"emg-{channel}.csv")

                pipeline = SavingPipelineFactory().create(
                    source_queue=queue, filename=filename
                )
                pipelines.append(pipeline)

            channel_sink = ConditionalSink(
                SinkList(channel_sinks), ChannelSelection(channel)
            )
            processing_sinks.append(channel_sink)

        processing_pipeline = ProcessingPipelineFactory().create(
            in_queue=source_out_queue, sink=SinkList(processing_sinks)
        )
        pipelines.append(processing_pipeline)

        return MultiProcess(pipelines)
