from src.pipeline.executors.base import Executor, ExecutorFactory, FromSourceExecutor
from src.pipeline.handlers import FixedAccumulator, Animate, ExtractCharacteristics, HandlersList, Predict, Print, Time, TimedAccumulator, ToNumpy
from src.pipeline.sources import DataSource
from src.pipeline.types import Animator, CharacteristicsExtractor, Model
from src.utils.loggers import ConsoleLogger


class PredictionExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource, extractor: CharacteristicsExtractor, model: Model, animator: Animator = None) -> None:
        logger = ConsoleLogger(prefix='[prediction]')
        handlers = [
            # TODO choose the right accumulator
            FixedAccumulator(window_size=200),
            # TimedAccumulator(time_in_seconds=1/30),
            ToNumpy(),
            ExtractCharacteristics(extractor=extractor),
            Predict(model=model),
            Time(logger=logger, timeout=1),
        ]

        if animator:
            handlers.append(Animate(animator=animator))
        else:
            handlers.append(Print(logger=logger))

        self.__executor = FromSourceExecutor(source=source, handler=HandlersList(handlers))

    def create(self) -> Executor:
        return self.__executor
