from multiprocessing import Queue
from src.data.processes import ExecutorProcess
from src.utils.plot import BatchPlotUpdate, RefreshingPlot
from src.data.executors import ProcessesExecutor
from src.data.experiments import PlottingExperiment, CSVExperiment, SerialExperiment


plot = RefreshingPlot()
csv_queue = queue = Queue(maxsize=5000)
plot_queue = queue = Queue(maxsize=1000)

csv_experiment = CSVExperiment(queue=csv_queue)
plotting_experiment = PlottingExperiment(plot=plot, queue=plot_queue)
serial_experiment = SerialExperiment(
    csv_logger=csv_experiment.get_logger(),
    plot_logger=plotting_experiment.get_logger(),
    csv_queue=csv_queue,
    plot_queue=plot_queue
)

serial_process = ExecutorProcess(name='Serial', executor=serial_experiment.create_executor())
plotting_process = ExecutorProcess(name='Plotting', executor=plotting_experiment.create_executor())
csv_process = ExecutorProcess(name='CSV', executor=csv_experiment.create_executor())

executor = ProcessesExecutor(processes=[
    serial_process,
    plotting_process,
    csv_process,
], wait_for_ending=True)

executor.execute()
