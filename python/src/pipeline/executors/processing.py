from src.pipeline.executors.base import (
    Executor,
    ExecutorFactory,
    FromSourceExecutor,
    Retryer,
)
from src.pipeline.handlers import (
    DataHandler,
    HandlersList,
    ProcessFromUART,
    Time,
    TimeChecker,
    ToInt,
)
from src.pipeline.sources import DataSource
from src.utils.loggers import ConsoleLogger


class ProcessingExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource, output_handler: DataHandler) -> None:
        self.__source = source
        self.__output_handler = output_handler

    def create(self) -> Executor:
        logger = ConsoleLogger(name="processing")
        handler = HandlersList(
            [
                ProcessFromUART(),
                ToInt(),
                Time(logger=logger, timeout=5),
                self.__output_handler,
                TimeChecker(),
                # Print(logger=ConsoleLogger()),
            ]
        )

        executor = FromSourceExecutor(source=self.__source, handler=handler)
        executor = Retryer(executor=executor, nb_retries=1)

        return executor
