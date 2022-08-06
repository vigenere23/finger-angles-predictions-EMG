import os
from typing import List

import numpy as np
from modupipe.queue import GetBlocking, PutNonBlocking, Queue
from modupipe.runnable import Pipeline, Retry, Runnable, NamedRunnable
from modupipe.sink import Printer, QueueSink, Sink, SinkList
from modupipe.source import QueueSource, SourceList

from src.pipeline2.csv import CSVWriter, WithoutChannel
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
from src.pipeline2.sinks import LogRate, LogTime, Plot
from src.pipeline.data import ProcessedData, RangeData, SerialData
from src.pipeline.types import CharacteristicsExtractor, PredictionModel
from src.utils.loggers import ConsoleLogger
from src.utils.plot import RefreshingPlot, TimedPlotUpdate


class FilteringPipelineFactory:
    def create(
        self, in_queue: Queue[ProcessedData[int]], sink: Sink[ProcessedData[int]]
    ) -> Runnable:
        source = QueueSource(in_queue, strategy=GetBlocking())
        mapper = NotchDC(R=0.99) + NotchFrequencyOnline(
            frequency=60, sampling_frequency=2500
        )

        return NamedRunnable("Filtering pipeline", Pipeline(source + mapper, sink))


class SourcePipelineFactory:
    def create(self, serial_port: str, out_queue: Queue[SerialData[bytes]]) -> Runnable:
        source = SerialSourceFactory().create(port=serial_port)
        sink = QueueSink(out_queue, strategy=PutNonBlocking())

        pipeline = Pipeline(source, sink)
        return NamedRunnable("Serial source pipeline", Retry(pipeline, nb_times=10))


class ProcessingPipelineFactory:
    def create(
        self,
        in_queue: Queue[SerialData[bytes]],
        sink: Sink[ProcessedData[int]],
    ) -> Runnable:
        logger = ConsoleLogger(name="processing")

        source = QueueSource(in_queue, strategy=GetBlocking())
        mapper = ProcessFromSerial() + ToInt()
        sinks = SinkList([sink, LogRate(logger=logger), LogTime(logger=logger)])

        pipeline = Pipeline(source + mapper, sinks)
        return NamedRunnable("Processing pipeline", Retry(pipeline, nb_times=1))


class SavingPipelineFactory:
    def create(
        self,
        channel: int,
        source_queue: Queue[ProcessedData[int]],
        experiment_path: str,
    ) -> Runnable:
        source = QueueSource(source_queue, strategy=GetBlocking())

        filename = os.path.join(experiment_path, f"emg-{channel}.csv")
        sink = CSVWriter[ProcessedData[int]](
            file=filename, batch_size=100, strategy=WithoutChannel()
        )

        return NamedRunnable("CSV saving pipeline", Pipeline(source, sink))


class PlottingPipelineFactory:
    def create(self, channel: int, source_queue: Queue[ProcessedData[int]]) -> Runnable:
        source = QueueSource(source_queue, strategy=GetBlocking())

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
        sink = Plot(plot_strategy)

        return NamedRunnable("Plotting pipeline", Pipeline(source, sink))


class ExtractionPipelineFactory:
    def create(
        self,
        in_queue: Queue[ProcessedData[int]],
        out_queue: Queue[RangeData[np.ndarray]],
        extractor: CharacteristicsExtractor,
    ):
        logger = ConsoleLogger(name="extractor")
        source = QueueSource(in_queue, strategy=GetBlocking())
        mapper = (
            TimedBuffer(time_in_seconds=1 / 10)
            + ToNumpy(to2D=True)
            + ExtractCharacteristics(extractor=extractor)
            + ToNumpy(flatten=True)
            + Log(logger)
        )
        sink = QueueSink(out_queue, strategy=PutNonBlocking())

        return NamedRunnable("Extraction pipeline", Pipeline(source + mapper, sink))


class PredictionPipelineFactory:
    def create(
        self, in_queues: List[Queue[RangeData[np.ndarray]]], model: PredictionModel
    ):
        logger = ConsoleLogger(name="prediction")
        source = SourceList(
            [QueueSource(queue, strategy=GetBlocking()) for queue in in_queues]
        )
        mapper = MergeRangeData() + ToNumpy() + Predict(model=model) + Log(logger)
        sink = Printer()

        return NamedRunnable("Prediction pipeline", Pipeline(source + mapper, sink))
