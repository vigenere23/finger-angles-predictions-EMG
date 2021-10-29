from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor, Retryer
from src.pipeline.handlers import DataHandler, ProcessFromUART, Time, ToInt
from src.pipeline.sources import DataSource
from src.utils.loggers import ConsoleLogger


class ProcessingExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource) -> None:
        self.__source = source
        self.__output_handlers = []

    def add_output(self, handler: DataHandler):
        self.__output_handlers.append(handler)

    def create(self) -> Executor:
        logger = ConsoleLogger(prefix="[processing]")
        handlers = [
            ProcessFromUART(),
            ToInt(),
            Time(logger=logger, timeout=5),
            *self.__output_handlers,
        ]

        executor = HandlersExecutor(source=self.__source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor
