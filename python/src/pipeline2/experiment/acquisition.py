import multiprocessing
import os
import pathlib
from datetime import datetime
from typing import List

from modupipe.loader import LoaderList, OnCondition, PutToQueue, Sink
from modupipe.queue import PutNonBlocking, Queue
from modupipe.runnable import MultiProcess, Runnable

from src.pipeline2.conditions import ChannelSelection
from src.pipeline2.experiment.pipelines import (
    FilteringPipelineFactory,
    PlottingPipelineFactory,
    ProcessingPipelineFactory,
    SavingPipelineFactory,
    SourcePipelineFactory,
)
from src.pipeline.data import ProcessedData, SerialData


class AcquisitionExperimentFactory:
    """Creates the acquisition experiment pipeline.

    Pipeline architecture :
    ```
    serial ─⏵ processing ┬─⏵ filtering ch.1 ┬─⏵ [csv]
                         │                  └─⏵ [plot]
                         └─⏵ filtering ch.2 ┬─⏵ [csv]
                                            └─⏵ [plot]
    ```
    """

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
            channel_filtering_sinks: List[Sink[ProcessedData[int]]] = []

            if channel in plotting_channels:
                queue = Queue(multiprocessing.Queue())
                channel_filtering_sinks.append(
                    PutToQueue(queue, strategy=PutNonBlocking())
                )
                pipeline = PlottingPipelineFactory().create(
                    channel=channel, source_queue=queue
                )
                pipelines.append(pipeline)

            if channel in saving_channels:
                queue = Queue(multiprocessing.Queue())
                channel_filtering_sinks.append(
                    PutToQueue(queue, strategy=PutNonBlocking())
                )

                pipeline = SavingPipelineFactory().create(
                    channel=channel, source_queue=queue, experiment_path=experiment_path
                )
                pipelines.append(pipeline)

            channel_processing_out_queue = Queue(multiprocessing.Queue())
            channel_processing_sink = OnCondition(
                ChannelSelection(channel),
                PutToQueue(channel_processing_out_queue, strategy=PutNonBlocking()),
            )
            processing_sinks.append(channel_processing_sink)

            channel_filtering_pipeline = FilteringPipelineFactory().create(
                in_queue=channel_processing_out_queue,
                loader=LoaderList(channel_filtering_sinks),
            )
            pipelines.append(channel_filtering_pipeline)

        processing_pipeline = ProcessingPipelineFactory().create(
            in_queue=source_out_queue, sink=LoaderList(processing_sinks)
        )
        pipelines.append(processing_pipeline)

        return MultiProcess(pipelines)
