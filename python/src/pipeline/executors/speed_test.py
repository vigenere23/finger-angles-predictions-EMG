from src.pipeline.executors.base import Executor, FromSourceExecutor, ProcessesExecutor, Retryer
from src.pipeline.handlers import HandlersList, ProcessFromUART, Time, ToInt
from src.pipeline.processes import ExecutorProcess
from src.pipeline.sources import SerialSource
from src.utils.loggers import ConsoleLogger


class SpeedTest(Executor):
    def __init__(self, serial_port: str) -> None:
        self.__port = serial_port
    
    def execute(self):
        logger = ConsoleLogger(prefix="[speed-test]")
        source = SerialSource(
            port=self.__port,
            baudrate=115200,
            sync_byte=b'\n',
            check_byte=b'\xff',
            logger=None,
        )
        handler = HandlersList([
            ProcessFromUART(),
            ToInt(),
            Time(logger=logger, timeout=5),
        ])

        executor = FromSourceExecutor(source=source, handler=handler)
        executor = Retryer(executor=executor, nb_retries=5)
        process = ExecutorProcess(name='Speed test', executor=executor)
        executor = ProcessesExecutor(processes=[
            process
        ])

        executor.execute()
