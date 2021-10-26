from src.data.executors import HandlersExecutor, ProcessesExecutor, Retryer
from src.data.handlers import Print, ProcessFromUART, Time, ToInt
from src.data.processes import ExecutorProcess
from src.data.sources import SerialDataSource
from src.utils.loggers import ConsoleLogger


logger = ConsoleLogger(prefix="[speed-test]")
source = SerialDataSource(
    port='/dev/ttyACM1',
    baudrate=115200,
    start_byte=b'\x01',
    stop_byte=b'\xfe',
    message_size=4,
    batch_size=10
)
handlers = [
    ProcessFromUART(),
    ToInt(),
    Time(logger=logger),
    # Print(logger=logger)
]

executor = HandlersExecutor(source=source, handlers=handlers)
executor = Retryer(executor=executor, nb_retries=5)
process = ExecutorProcess(name='Speed test', executor=executor)
executor = ProcessesExecutor(processes=[
    process
], wait_for_ending=True)

executor.execute()
