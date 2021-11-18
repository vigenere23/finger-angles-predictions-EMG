from src.pipeline.executors.base import Executor, ExecutorFactory, FromSourceExecutor
from src.pipeline.handlers import Plot
from src.pipeline.sources import DataSource
from src.utils.plot import RefreshingPlot, TimedPlotUpdate


class PlottingExecutorFactory(ExecutorFactory):
    def __init__(self, plot: RefreshingPlot, source: DataSource, n_ys: int, window_size: int) -> None:
        plot_strategy = TimedPlotUpdate(plot=plot, n_ys=n_ys, window_size=window_size, update_time=1)
        handler = Plot(strategy=plot_strategy)

        self.__executor = FromSourceExecutor(source=source, handler=handler)

    def create(self) -> Executor:
        return self.__executor
