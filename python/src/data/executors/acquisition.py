import os
from pathlib import Path
from datetime import datetime
from multiprocessing import Queue
from typing import List
from src.data.executors.base import Executor, ExecutorFactory, ProcessesExecutor
from src.data.executors.csv import CSVExecutorFactory
from src.data.executors.plotting import PlottingExecutorFactory
from src.data.executors.processing import ProcessingExecutorFactory
from src.data.executors.queues import QueuesExecutorFactory
from src.data.executors.serial import SerialExecutorFactory
from src.data.handlers import AddToQueue
from src.data.processes import ExecutorProcess, SleepingExecutorProcess
from src.data.sources import QueueSource
from src.utils.plot import RefreshingPlot
from src.utils.queues import BlockingFetch, NamedQueue, NonBlockingPut


class AcquisitionExperiment(Executor):
    def __init__(self, serial_port: str):
        processing_queue = NamedQueue(name='processing', queue=Queue())

        self.__serial = SerialExecutorFactory(port=serial_port)
        self.__serial.add_output(
            AddToQueue(queue=processing_queue, strategy=NonBlockingPut())
        )
        
        self.__processing = ProcessingExecutorFactory(
            source=QueueSource(queue=processing_queue, strategy=BlockingFetch())
        )

        self.__queues = [processing_queue]
        self.__plottings: List[ExecutorFactory] = []
        self.__csv: ExecutorFactory = None

    def add_csv_saving(self):
        path = os.path.join(Path.cwd(), 'data', str(datetime.now().timestamp()), 'emg.csv')
        queue = NamedQueue(name=f'csv', queue=Queue())
        self.__processing.add_output(
            AddToQueue(queue=queue, strategy=NonBlockingPut())
        )

        self.__csv = CSVExecutorFactory(
            source=QueueSource(queue=queue, strategy=BlockingFetch()),
            path=path
        )

        self.__queues.append(queue)

    def add_plotting(self, channel: int):
        queue = NamedQueue(name=f'plot-{channel}', queue=Queue())
        self.__processing.add_output(
            AddToQueue(queue=queue, strategy=NonBlockingPut())
        )

        plot = RefreshingPlot(
            title=f'UART data from channel {channel}',
            x_label='time',
            y_label='value',
        )
        plotting = PlottingExecutorFactory(
            plot=plot,
            source=QueueSource(queue=queue, strategy=BlockingFetch()),
            channel=channel
        )

        self.__plottings.append(plotting)
        self.__queues.append(queue)

    def execute(self):
        processes = [
            ExecutorProcess(name='Serial', executor=self.__serial.create()),
            ExecutorProcess(name='Processing', executor=self.__processing.create())
        ]

        for i, plotting in enumerate(self.__plottings):
            processes.append(
                ExecutorProcess(name=f'Plotting {i}', executor=plotting.create())
            )

        if self.__csv:
            processes.append(ExecutorProcess(name='CSV', executor=self.__csv.create()))
        
        processes.append(
            SleepingExecutorProcess(
                name='Queues',
                executor=QueuesExecutorFactory(queues=self.__queues).create(),
                sleep_time=5
            )
        )

        executor = ProcessesExecutor(processes=processes, wait_for_ending=True)
        executor.execute()
