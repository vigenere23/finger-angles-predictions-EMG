from src.pipeline.executors.base import Executor, ExecutorFactory, FromSourceExecutor
from src.pipeline.savers import CSVWriter, WithoutChannel
from src.pipeline.sources import DataSource


class CSVExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource, path: str) -> None:
        handler = CSVWriter(file=path, batch_size=100, strategy=WithoutChannel())
        # handler = CSVWriter(file=path, batch_size=100, strategy=ValueOnly())

        self.__executor = FromSourceExecutor(source=source, handler=handler)

    def create(self) -> Executor:
        return self.__executor
