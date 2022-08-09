import multiprocessing
from typing import List

import numpy as np
from modupipe.loader import LoaderList, OnCondition, PutToQueue, Sink
from modupipe.queue import PutNonBlocking, Queue
from modupipe.runnable import MultiProcess, Runnable

from src.ai.transform_unique import FeaturesTransformEMG
from src.ai.utilities import load_model
from src.pipeline.conditions import ChannelSelection
from src.pipeline.data import ProcessedData, RangeData, SerialData
from src.pipeline.experiment.pipelines import (
    ExtractionPipelineFactory,
    FilteringPipelineFactory,
    PlottingPipelineFactory,
    PredictionPipelineFactory,
    ProcessingPipelineFactory,
    SourcePipelineFactory,
)


class PredictionExperimentFactory:
    """Creates the prediction experiment pipeline.

    Pipeline architecture :
    ```
                                              ┌─⏵ [plot]
                          ┌─⏵ filtering ch.1 ─┴─⏵ extraction ┐
    serial ─⏵ processing ─┤                                  ├─⏵ prediction ─⏵ [animation]
                          └─⏵ filtering ch.2 ─┬─⏵ extraction ┘
                                              └─⏵ [plot]
    ```
    """

    def create(
        self,
        serial_port: str,
        model_name: str,
        plotting_channels: List[int] = [],
        predicting_channels: List[int] = [],
    ) -> Runnable:
        pipelines: List[Runnable] = []

        source_out_queue = Queue[SerialData[bytes]](
            multiprocessing.Queue()
        )  # TODO maxsize?

        source_pipeline = SourcePipelineFactory().create(
            serial_port=serial_port, out_queue=source_out_queue
        )
        pipelines.append(source_pipeline)

        processing_sinks: List[Sink[ProcessedData[int]]] = []
        used_channels = set(plotting_channels + predicting_channels)

        extraction_out_queues: List[Queue[RangeData[np.ndarray]]] = []

        for channel in used_channels:
            filtering_sinks: List[Sink[ProcessedData[int]]] = []

            if channel in plotting_channels:
                plotting_in_queue = Queue(multiprocessing.Queue())
                filtering_sinks.append(
                    PutToQueue(plotting_in_queue, strategy=PutNonBlocking())
                )
                pipeline = PlottingPipelineFactory().create(
                    channel=channel, source_queue=plotting_in_queue
                )
                pipelines.append(pipeline)

            if channel in predicting_channels:
                extraction_in_queue = Queue(multiprocessing.Queue())
                filtering_sinks.append(
                    PutToQueue(extraction_in_queue, strategy=PutNonBlocking())
                )

                extraction_out_queue = Queue(multiprocessing.Queue())
                extraction_out_queues.append(extraction_out_queue)

                pipeline = ExtractionPipelineFactory().create(
                    in_queue=extraction_in_queue,
                    out_queue=extraction_out_queue,
                    extractor=FeaturesTransformEMG(),
                )
                pipelines.append(pipeline)

            processing_out_queue = Queue(multiprocessing.Queue())
            processing_sink = OnCondition(
                ChannelSelection(channel),
                PutToQueue(processing_out_queue, strategy=PutNonBlocking()),
            )
            processing_sinks.append(processing_sink)

            filtering_pipeline = FilteringPipelineFactory().create(
                in_queue=processing_out_queue,
                loader=LoaderList(filtering_sinks),
            )
            pipelines.append(filtering_pipeline)

            if len(extraction_out_queues) != 0:
                prediction_pipeline = PredictionPipelineFactory().create(
                    in_queues=extraction_out_queues,
                    model=load_model(model_name=model_name),
                )
                pipelines.append(prediction_pipeline)

        processing_pipeline = ProcessingPipelineFactory().create(
            in_queue=source_out_queue, sink=LoaderList(processing_sinks)
        )
        pipelines.append(processing_pipeline)

        return MultiProcess(pipelines)
