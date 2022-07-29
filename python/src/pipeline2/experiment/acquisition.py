from typing import List

from modupipe.queue import GetBlocking, PutNonBlocking, Queue
from modupipe.runnable import MultiProcess, Pipeline, Retry, Runnable
from modupipe.sink import QueueSink, Sink, SinkList
from modupipe.source import QueueSource

from src.pipeline2.mappers import Log, ProcessFromSerial, TimeChecker, ToInt
from src.pipeline2.sinks import ChannelSelection
from src.pipeline2.sources import SerialSourceFactory
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
        out_queue: Queue[ProcessedData[int]],
    ) -> Runnable:
        logger = ConsoleLogger(prefix="[processing]")

        source = QueueSource(in_queue, strategy=GetBlocking())
        mapper = ProcessFromSerial() + ToInt() + Log(logger) + TimeChecker()
        sink = QueueSink(out_queue, strategy=PutNonBlocking())

        pipeline = Pipeline(source + mapper, sink)
        return Retry(pipeline, nb_times=1)


class AcquisitionExperimentFactory:
    def create(
        self,
        serial_port: str,
        plotting_channels: List[int] = [],
        saving_channels: List[int] = [],
    ) -> Runnable:
        source_out_queue = Queue[SerialData[bytes]]()
        processing_out_queue = Queue[ProcessedData[int]]()

        source_pipeline = SourcePipelineFactory().create(
            serial_port=serial_port, out_queue=source_out_queue
        )
        processing_pipeline = ProcessingPipelineFactory().create(
            in_queue=source_out_queue, out_queue=processing_out_queue
        )

        sinks: List[Sink[ProcessedData]] = []
        used_channels = set(plotting_channels + saving_channels)

        for channel in used_channels:
            channel_sinks: List[Sink[ProcessedData]] = []

            if channel in plotting_channels:
                pass  # TODO setup channel plotting

            if channel in saving_channels:
                pass  # TODO setup channel saving

            channel_sink = ChannelSelection(channel, SinkList(channel_sinks))
            sinks.append(channel_sink)

        return MultiProcess([source_pipeline, processing_pipeline])
