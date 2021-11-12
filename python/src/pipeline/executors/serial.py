from typing import List
from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor, Retryer
from src.pipeline.handlers import DataHandler
from src.pipeline.sources import RandomFakeSerialSource, FrequencyFakeSerialSource, SerialDataSource
from src.utils.loggers import ConsoleLogger


class SerialExecutorFactory(ExecutorFactory):
    def __init__(self, port: str, output_handlers: List[DataHandler]) -> None:
        logger = ConsoleLogger(prefix="[serial]")

        if port == 'fake':
            self.__source = RandomFakeSerialSource()
        elif port == 'freq':
            self.__source = FrequencyFakeSerialSource()
        else:
            self.__source = SerialDataSource(
                port=port,
                baudrate=115200,
                sync_byte=b'\n',
                check_byte=b'\xFF',
                # use_parity=True, TODO parity not working
                logger=logger,
                # verbose=True
            )

        self.__output_handlers = output_handlers
        
    def create(self) -> Executor:
        handlers = [
            *self.__output_handlers,
        ]

        executor = HandlersExecutor(source=self.__source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor
