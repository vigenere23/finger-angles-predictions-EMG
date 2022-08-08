import os
from typing import List

import numpy as np
from modupipe.extractor import ExtractorList, GetFromQueue
from modupipe.loader import LoaderList, PutToQueue, Sink
from modupipe.mapper import PushTo
from modupipe.queue import GetBlocking, PutNonBlocking, Queue
from modupipe.runnable import FullPipeline, NamedRunnable, Retry, Runnable

from src.pipeline2.csv import CSVWriter, WithoutChannel
from src.pipeline2.loaders import LogRate, LogTime, Plot
from src.pipeline2.mappers import (
    ExtractCharacteristics,
    Log,
    MergeRangeData,
    NotchDC,
    NotchFrequencyOnline,
    Predict,
    ProcessFromSerial,
    TimedBuffer,
    ToInt,
    ToNumpy,
)
from src.pipeline2.serial import SerialSourceFactory
from src.pipeline.data import ProcessedData, RangeData, SerialData
from src.pipeline.types import CharacteristicsExtractor, PredictionModel
from src.utils.loggers import ConsoleLogger
from src.utils.plot import RefreshingPlot, TimedPlotUpdate


class FilteringPipelineFactory:
    def create(
        self, in_queue: Queue[ProcessedData[int]], loader: Sink[ProcessedData[int]]
    ) -> Runnable:
        source = GetFromQueue(in_queue, strategy=GetBlocking())
        mapper = NotchDC(R=0.99) + NotchFrequencyOnline(
            frequency=60, sampling_frequency=2500
        )

        return NamedRunnable(
            "Filtering pipeline", FullPipeline(source + mapper + PushTo(loader))
        )


class SourcePipelineFactory:
    def create(self, serial_port: str, out_queue: Queue[SerialData[bytes]]) -> Runnable:
        source = SerialSourceFactory().create(port=serial_port)
        loader = PutToQueue(out_queue, strategy=PutNonBlocking())

        pipeline = FullPipeline(source + PushTo(loader))
        return NamedRunnable("Serial source pipeline", Retry(pipeline, nb_times=10))


class ProcessingPipelineFactory:
    def create(
        self,
        in_queue: Queue[SerialData[bytes]],
        sink: Sink[ProcessedData[int]],
    ) -> Runnable:
        logger = ConsoleLogger(name="processing")

        source = GetFromQueue(in_queue, strategy=GetBlocking())
        mapper = ProcessFromSerial() + ToInt()
        loader = LoaderList([sink, LogRate(logger=logger), LogTime(logger=logger)])

        pipeline = FullPipeline(source + mapper + PushTo(loader))
        return NamedRunnable("Processing pipeline", Retry(pipeline, nb_times=1))


class SavingPipelineFactory:
    def create(
        self,
        channel: int,
        source_queue: Queue[ProcessedData[int]],
        experiment_path: str,
    ) -> Runnable:
        source = GetFromQueue(source_queue, strategy=GetBlocking())

        filename = os.path.join(experiment_path, f"emg-{channel}.csv")
        loader = CSVWriter[ProcessedData[int]](
            file=filename, batch_size=100, strategy=WithoutChannel()
        )

        return NamedRunnable(
            "CSV saving pipeline", FullPipeline(source + PushTo(loader))
        )


class PlottingPipelineFactory:
    def create(self, channel: int, source_queue: Queue[ProcessedData[int]]) -> Runnable:
        source = GetFromQueue(source_queue, strategy=GetBlocking())

        plot = RefreshingPlot(
            series=["original", "filtered"],
            title=f"Data from channel {channel}",
            x_label="time",
            y_label="value",
        )
        plot_strategy = TimedPlotUpdate(
            plot=plot,
            n_ys=2,
            window_size=2000,
            update_time=0.5,
            plot_time=False,
        )
        loader = Plot(plot_strategy)

        return NamedRunnable("Plotting pipeline", FullPipeline(source + PushTo(loader)))


class ExtractionPipelineFactory:
    def create(
        self,
        in_queue: Queue[ProcessedData[int]],
        out_queue: Queue[RangeData[np.ndarray]],
        extractor: CharacteristicsExtractor,
    ):
        logger = ConsoleLogger(name="extractor")
        source = GetFromQueue(in_queue, strategy=GetBlocking())
        mapper = (
            TimedBuffer(time_in_seconds=1 / 10)
            + ToNumpy(to2D=True)
            + ExtractCharacteristics(extractor=extractor)
            + ToNumpy(flatten=True)
            + Log(logger)
        )
        loader = PutToQueue(out_queue, strategy=PutNonBlocking())

        return NamedRunnable(
            "Extraction pipeline", FullPipeline(source + mapper + PushTo(loader))
        )


class PredictionPipelineFactory:
    def create(
        self, in_queues: List[Queue[RangeData[np.ndarray]]], model: PredictionModel
    ):
        logger = ConsoleLogger(name="prediction")
        source = ExtractorList(
            [GetFromQueue(queue, strategy=GetBlocking()) for queue in in_queues]
        )
        mapper = MergeRangeData() + ToNumpy() + Predict(model=model) + Log(logger)

        return NamedRunnable("Prediction pipeline", FullPipeline(source + mapper))
