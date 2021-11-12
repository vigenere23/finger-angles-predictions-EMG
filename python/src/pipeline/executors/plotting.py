from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor
from src.pipeline.handlers import ChannelSelector, Plot
from src.pipeline.sources import DataSource
from src.utils.plot import BatchPlotUpdate, RefreshingPlot, TimedPlotUpdate


class PlottingExecutorFactory(ExecutorFactory):
    def __init__(self, plot: RefreshingPlot, source: DataSource, channel: int) -> None:
        plot_strategy = TimedPlotUpdate(plot=plot, window_size=500, update_time=1)

        handlers = [
            ChannelSelector(channel=channel),
            Plot(strategy=plot_strategy),
        ]

        self.__executor = HandlersExecutor(source=source, handlers=handlers)

    def create(self) -> Executor:
        return self.__executor
