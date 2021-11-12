import os
from pathlib import Path
from datetime import datetime
from multiprocessing import Queue
from typing import Dict
from src.pipeline.executors.base import Executor, ExecutorFactory, ProcessesExecutor
from src.pipeline.executors.csv import CSVExecutorFactory
from src.pipeline.executors.plotting import PlottingExecutorFactory
from src.pipeline.executors.processing import ProcessingExecutorFactory
from src.pipeline.executors.queues import QueuesExecutorFactory
from src.pipeline.executors.serial import SerialExecutorFactory
from src.pipeline.handlers import AddToQueue, BranchedHandlers, ChannelSelector
from src.pipeline.processes import ExecutorProcess, SleepingExecutorProcess
from src.pipeline.sources import QueueSource
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
        self.__future_processes: Dict[str, ExecutorFactory] = {}

    def add_csv_saving(self):
        path = os.path.join(Path.cwd(), 'data', str(datetime.now().timestamp()), 'emg.csv')
        queue = NamedQueue(name=f'csv', queue=Queue())
        self.__processing.add_output(
            AddToQueue(queue=queue, strategy=NonBlockingPut())
        )

        csv = CSVExecutorFactory(
            source=QueueSource(queue=queue, strategy=BlockingFetch()),
            path=path
        )

        self.__future_processes['CSV'] = csv
        self.__queues.append(queue)

    def add_plotting(self, channel: int):
        queue = NamedQueue(name=f'plot-{channel}', queue=Queue())
        self.__processing.add_output(
            BranchedHandlers(handlers=[
                ChannelSelector(channel=channel),
                AddToQueue(queue=queue, strategy=NonBlockingPut())
            ])
        )

        plot = RefreshingPlot(
            title=f'UART data from channel {channel}',
            x_label='time',
            y_label='value',
        )
        plotting = PlottingExecutorFactory(
            plot=plot,
            source=QueueSource(queue=queue, strategy=BlockingFetch())
        )

        self.__future_processes[f'Plot-{channel}'] = plotting
        self.__queues.append(queue)

    def execute(self):
        processes = [
            ExecutorProcess(name='Serial', executor=self.__serial.create()),
            ExecutorProcess(name='Processing', executor=self.__processing.create())
        ]

        for process_name, executor_factory in self.__future_processes.items():
            processes.append(ExecutorProcess(
                name=process_name,
                executor=executor_factory.create()
            ))
        
        processes.append(
            SleepingExecutorProcess(
                name='Queues',
                executor=QueuesExecutorFactory(queues=self.__queues).create(),
                sleep_time=5
            )
        )

        executor = ProcessesExecutor(processes=processes, wait_for_ending=True)
        executor.execute()
