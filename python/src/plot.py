from typing import Any
import numpy as np
from contextlib import contextmanager
from matplotlib import pyplot as plt
from src.data import DataSource


@contextmanager
def plotting_figure():
    plt.figure()

    yield plt

    plt.legend()


@contextmanager
def plotting():
    yield None

    plt.show()


class LivePlotter:
    def __init__(self, title: str = '', x_label: str = '', y_label: str = ''):
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.ticklabel_format(useOffset=False, style='plain')
        self.__line, = ax.plot([0], [0])

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(title)

        plt.xlim([0, 1])
        
        plt.show()

    def update(self, x, y):
        self.__line.set_xdata(x)
        self.__line.set_ydata(y)

        std_y = np.std(y)

        plt.xlim([np.min(x), np.max(x)])
        plt.ylim([np.min(y) - std_y, np.max(y) + std_y])

        plt.pause(0.1)


class BufferedLivePlotter:
    def __init__(self, plotter: LivePlotter, buffer_size: int, source: DataSource[Any], in_batch: bool = False):
        x = np.linspace(0, 1, buffer_size)
        y = [0] * buffer_size
        plotter.update(x, y)

        self.__plotter = plotter
        self.__size = buffer_size
        self.__x = x
        self.__y = y
        self.__source = source
        self.__in_batch = in_batch

    def update(self):
        if self.__in_batch:
            self.__y = self.__source.get()
        else:
            for i in range(self.__size):
                self.__y[i] = self.__source.get()

        self.__plotter.update(self.__x, self.__y)
