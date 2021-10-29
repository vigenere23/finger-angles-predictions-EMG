from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor, Retryer
from src.pipeline.handlers import DataHandler
from src.pipeline.sources import SerialDataSource
from src.utils.loggers import ConsoleLogger


class SerialExecutorFactory(ExecutorFactory):
    def __init__(self, port: str) -> None:
        logger = ConsoleLogger(prefix="[serial]")

        if port == 'fake':
            pass # TODO add fake serial source
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

        self.__output_handlers = []
        

    def add_output(self, handler: DataHandler):
        self.__output_handlers.append(handler)


    def create(self) -> Executor:
        handlers = [
            *self.__output_handlers,
        ]

        executor = HandlersExecutor(source=self.__source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor
