from src.pipeline.executors.base import Executor, HandlersExecutor, ProcessesExecutor, Retryer
from src.pipeline.handlers import ProcessFromUART, Time, ToInt
from src.pipeline.processes import ExecutorProcess
from src.pipeline.sources import SerialDataSource
from src.utils.loggers import ConsoleLogger


class SpeedTest(Executor):
    def __init__(self, serial_port: str) -> None:
        self.__port = serial_port
    
    def execute(self):
        logger = ConsoleLogger(prefix="[speed-test]")
        source = SerialDataSource(
            port=self.__port,
            baudrate=115200,
            sync_byte=b'\n',
            check_byte=b'\xff',
            logger=None,
        )
        handlers = [
            ProcessFromUART(),
            ToInt(),
            Time(logger=logger),
        ]

        executor = HandlersExecutor(source=source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=5)
        process = ExecutorProcess(name='Speed test', executor=executor)
        executor = ProcessesExecutor(processes=[
            process
        ], wait_for_ending=True)

        executor.execute()