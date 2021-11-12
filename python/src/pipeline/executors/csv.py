from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor
from src.pipeline.savers import CSVWriter, Complete
from src.pipeline.sources import DataSource


class CSVExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource, path: str) -> None:
        handlers = [
            CSVWriter(file=path, batch_size=100, strategy=Complete())
        ]

        self.__executor = HandlersExecutor(source=source, handlers=handlers)
    
    def create(self) -> Executor:
        return self.__executor
