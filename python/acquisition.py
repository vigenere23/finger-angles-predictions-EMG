from multiprocessing import Queue
from src.data.processes import ExecutorProcess, SleepingExecutorProcess
from src.utils.plot import BatchPlotUpdate, RefreshingPlot
from src.data.executors import ProcessesExecutor
from src.data.experiments import PlottingExperiment, CSVExperiment, QueuesAnalyzer, SerialExperiment
from src.utils.queues import NamedQueue


PLOT_QUEUE_SIZE = 1000
CSV_QUEUE_SIZE = 5000

plot = RefreshingPlot()
csv_queue = NamedQueue(name='csv', maxsize=CSV_QUEUE_SIZE, queue=Queue(maxsize=CSV_QUEUE_SIZE))
plot_queue = NamedQueue(name='plot', maxsize=PLOT_QUEUE_SIZE, queue=Queue(maxsize=PLOT_QUEUE_SIZE))

csv_experiment = CSVExperiment(queue=csv_queue)
plotting_experiment = PlottingExperiment(plot=plot, queue=plot_queue)
serial_experiment = SerialExperiment(
    csv_queue=csv_queue,
    plot_queue=plot_queue
)
queues_executor = QueuesAnalyzer(queues=[csv_queue, plot_queue])

serial_process = ExecutorProcess(name='Serial', executor=serial_experiment.create_executor())
plotting_process = ExecutorProcess(name='Plotting', executor=plotting_experiment.create_executor())
csv_process = ExecutorProcess(name='CSV', executor=csv_experiment.create_executor())
queues_check_process = SleepingExecutorProcess(name='Queues', executor=queues_executor, sleep_time=0.5)

executor = ProcessesExecutor(processes=[
    serial_process,
    plotting_process,
    csv_process,
    queues_check_process
], wait_for_ending=True)

executor.execute()
