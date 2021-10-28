from src.data.executors.base import Executor, ExecutorFactory, HandlersExecutor
from src.data.handlers import ChannelSelector, Plot
from src.data.sources import DataSource
from src.utils.plot import BatchPlotUpdate, RefreshingPlot


class PlottingExecutorFactory(ExecutorFactory):
    def __init__(self, plot: RefreshingPlot, source: DataSource, channel: int) -> None:
        plot_strategy = BatchPlotUpdate(plot=plot, window_size=40, batch_size=500)
        # self.__plot_strategy = FixedTimeUpdate(plot=plot, timeout=2, batch_size=30)

        handlers = [
            ChannelSelector(channel=channel),
            Plot(strategy=plot_strategy),
        ]

        self.__executor = HandlersExecutor(source=source, handlers=handlers)

    def create(self) -> Executor:
        return self.__executor
