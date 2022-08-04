import os

from modupipe.queue import GetBlocking, PutNonBlocking, Queue
from modupipe.runnable import Pipeline, Retry, Runnable
from modupipe.sink import QueueSink, Sink, SinkList
from modupipe.source import QueueSource

from src.pipeline2.csv import CSVWriter, WithoutChannel
from src.pipeline2.mappers import (
    NotchDC,
    NotchFrequencyOnline,
    ProcessFromSerial,
    ToInt,
)
from src.pipeline2.serial import SerialSourceFactory
from src.pipeline2.sinks import LogRate, LogTime, Plot
from src.pipeline.data import ProcessedData, SerialData
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

        return Pipeline(source + mapper, sink)


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
        mapper = ProcessFromSerial() + ToInt()
        sinks = SinkList([sink, LogRate(logger=logger), LogTime(logger=logger)])

        pipeline = Pipeline(source + mapper, sinks)
        return Retry(pipeline, nb_times=1)


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

        return Pipeline(source, sink)


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

        return Pipeline(source, sink)
