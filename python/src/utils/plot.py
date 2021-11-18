import numpy as np
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union
from matplotlib import pyplot as plt
from src.utils.lists import SizedFifo


class RefreshingPlot:
    def __init__(
            self,
            series: List[str],
            title: str = '',
            x_label: str = '',
            y_label: str = '',
            refresh_time: float = 0.01
    ):
        self.__title = title
        self.__x_label = x_label
        self.__y_label = y_label
        self.__refresh_time = refresh_time
        self.__init = False
        self.__series = series

    def __init_plot(self):
        if self.__init:
            return

        self.__init = True

        plt.ion()
        fig, ax = plt.subplots()
        ax.ticklabel_format(useOffset=False, style='plain')

        self.__ax = ax
        self.__lines = [ax.plot([0], [0], label=serie)[0] for serie in self.__series]

        ax.set_title(self.__title)
        ax.set_xlabel(self.__x_label)
        ax.set_ylabel(self.__y_label)
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        ax.legend()

        fig.show()
        plt.pause(0.1)

    def set_data(self, X: Union[list, np.array], Ys: List[Union[list, np.array]]):
        if not self.__init:
            self.__init_plot()

        for line, Y in zip(self.__lines, Ys):
            line.set_xdata(X)
            line.set_ydata(Y)

        plt.pause(self.__refresh_time)

    def resize(self, x: Tuple[float, float], y: Tuple[float, float]):
        if not self.__init:
            self.__init_plot()

        self.__ax.set_xlim(x[0], x[1])
        self.__ax.set_ylim(y[0], y[1])


class PlottingStrategy(ABC):
    @abstractmethod
    def update_plot(self, x: Any, ys: List[Any]):
        raise NotImplementedError()


class BatchPlotUpdate(PlottingStrategy):
    def __init__(self, plot: RefreshingPlot, window_size: int, batch_size: int, n_ys: int):
        self.__batch_size = batch_size
        self.__x_history = SizedFifo(size=window_size)
        self.__y_histories = [SizedFifo(size=window_size) for _ in range(n_ys)]
        self.__count = 0
        self.__plot = plot

    def update_plot(self, x: Any, ys: List[Any]):
        self.__x_history.append(x)
        for y, y_history in zip(ys, self.__y_histories):
            y_history.append(y)
        self.__count += 1
        
        if self.__count >= self.__batch_size:
            self.__count = 0

            X = self.__x_history.to_list()
            Ys = [y_history.to_list() for y_history in self.__y_histories]

            std_Y = max((np.std(Y) for Y in Ys))
            min_Y = min((np.min(Y) for Y in Ys))
            max_Y = max((np.max(Y) for Y in Ys))

            self.__plot.resize([np.min(X), np.max(X)], [min_Y - std_Y, max_Y + std_Y])
            self.__plot.set_data(X, Ys)


class TimedPlotUpdate(PlottingStrategy):
    def __init__(self, plot: RefreshingPlot, window_size: int, n_ys: int, update_time: float = 1):
        self.__x_history = SizedFifo(size=window_size)
        self.__y_histories = [SizedFifo(size=window_size) for _ in range(n_ys)]
        self.__plot = plot
        self.__update_time = update_time

        self.__start = datetime.now()

    def update_plot(self, x: Any, ys: List[Any]):
        self.__x_history.append(x)
        for y, y_history in zip(ys, self.__y_histories):
            y_history.append(y)

        deltatime = datetime.now() - self.__start
        
        if deltatime.total_seconds() >= self.__update_time:
            self.__start = datetime.now()

            Ys = [y_history.to_list() for y_history in self.__y_histories]
            # X = self.__x_history.to_list()
            X = list(range(len(Ys[0])))

            std_Y = max((np.std(Y) for Y in Ys))
            min_Y = min((np.min(Y) for Y in Ys))
            max_Y = max((np.max(Y) for Y in Ys))

            self.__plot.resize([np.min(X), np.max(X)], [min_Y - std_Y, max_Y + std_Y])
            self.__plot.set_data(X, Ys)


# TODO Not working
# class FixedTimeUpdate(PlottingStrategy):
#     def __init__(self, plot: RefreshingPlot, timeout: int, batch_size: int = 5):
#         self.__plot = plot
#         self.__timeout = timeout
#         self.__batch_size = batch_size

#         self.__X = []
#         self.__Y = []
#         self.__count = 0
#         self.__start = datetime.now()

#     def update_plot(self, x: Any, y: Any):
#         now = datetime.now()

#         if (now - self.__start).seconds >= self.__timeout:
#             self.__start = now

#             std_Y = np.std(self.__Y)
#             self.__plot.resize([self.__X[-1], self.__X[-1]+self.__timeout], [np.min(self.__Y) - std_Y, np.max(self.__Y) + std_Y])
#             self.__X = []
#             self.__Y = []

#         self.__X.append(x)
#         self.__Y.append(y)
#         self.__count += 1

#         if self.__count >= self.__batch_size:
#             self.__count = 0
#             self.__plot.set_data(self.__X, self.__Y)
