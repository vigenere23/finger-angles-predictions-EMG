from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor
from src.pipeline.savers import CSVWriter, ValueOnly, WithoutChannel
from src.pipeline.sources import DataSource


class CSVExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource, path: str) -> None:
        handlers = [
            CSVWriter(file=path, batch_size=100, strategy=WithoutChannel()),
            # CSVWriter(file=path, batch_size=100, strategy=ValueOnly()),
        ]

        self.__executor = HandlersExecutor(source=source, handlers=handlers)
    
    def create(self) -> Executor:
        return self.__executor
