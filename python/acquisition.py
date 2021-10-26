from multiprocessing import Queue
from src.data.processes import ExecutorProcess, SleepingExecutorProcess
from src.utils.plot import BatchPlotUpdate, RefreshingPlot
from src.data.executors import ProcessesExecutor
from src.data.experiments import PlottingExperiment, CSVExperiment, ProcessingExperiment, QueuesAnalyzer, SerialExperiment
from src.utils.queues import NamedQueue


DATA_QUEUE_SIZE = 1000
PLOT1_QUEUE_SIZE = 2000
PLOT2_QUEUE_SIZE = 2000
CSV_QUEUE_SIZE = 1000

plot1 = RefreshingPlot(
    title='UART data from channel 0',
    x_label='time',
    y_label='value',
)
plot2 = RefreshingPlot(
    title='UART data from channel 1',
    x_label='time',
    y_label='value',
)
data_queue = NamedQueue(name='serial', maxsize=DATA_QUEUE_SIZE, queue=Queue(maxsize=DATA_QUEUE_SIZE))
csv_queue = NamedQueue(name='csv', maxsize=CSV_QUEUE_SIZE, queue=Queue(maxsize=CSV_QUEUE_SIZE))
plot1_queue = NamedQueue(name='plot1', maxsize=PLOT1_QUEUE_SIZE, queue=Queue(maxsize=PLOT1_QUEUE_SIZE))
plot2_queue = NamedQueue(name='plot2', maxsize=PLOT2_QUEUE_SIZE, queue=Queue(maxsize=PLOT2_QUEUE_SIZE))

csv_experiment = CSVExperiment(queue=csv_queue)
plotting1_experiment = PlottingExperiment(channel=0, plot=plot1, queue=plot1_queue)
plotting2_experiment = PlottingExperiment(channel=1, plot=plot2, queue=plot2_queue)
serial_experiment = SerialExperiment(queue=data_queue)
processing_experiment = ProcessingExperiment(
    source_queue=data_queue,
    dispatch_queues=[csv_queue, plot1_queue, plot2_queue],
)
queues_executor = QueuesAnalyzer(queues=[
    data_queue, csv_queue, plot1_queue, plot2_queue
])

serial_process = ExecutorProcess(name='Serial', executor=serial_experiment.create_executor())
processing_process = ExecutorProcess(name='Processing', executor=processing_experiment.create_executor())
plotting1_process = ExecutorProcess(name='Plotting 1', executor=plotting1_experiment.create_executor())
plotting2_process = ExecutorProcess(name='Plotting 2', executor=plotting2_experiment.create_executor())
csv_process = ExecutorProcess(name='CSV', executor=csv_experiment.create_executor())
queues_check_process = SleepingExecutorProcess(name='Queues', executor=queues_executor, sleep_time=5)

executor = ProcessesExecutor(processes=[
    serial_process,
    processing_process,
    plotting1_process,
    plotting2_process,
    csv_process,
    queues_check_process
], wait_for_ending=True)

executor.execute()
