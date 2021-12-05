from typing import List
from src.pipeline.data import ProcessedData
from src.pipeline.executors.base import Executor, ExecutorFactory, FromSourceExecutor
from src.pipeline.handlers import ChannelSelection, ConditionalHandler, FixedAccumulator, Animate, ExtractCharacteristics, FixedRangeAccumulator, HandlersList, Predict, Print, Time, TimedAccumulator, ToNumpy
from src.pipeline.sources import DataSource
from src.pipeline.types import CharacteristicsExtractor, Model
from src.utils.loggers import ConsoleLogger


class PredictionExecutorFactory(ExecutorFactory):
    def __init__(self, source: DataSource[ProcessedData[int]], channels: List[int], extractor: CharacteristicsExtractor, model: Model, animate: bool = None) -> None:
        logger = ConsoleLogger(prefix='[prediction]')

        out_handlers = [
            FixedRangeAccumulator(size=len(channels)),
            ToNumpy(flatten=True),
            Predict(model=model),
            Time(logger=logger, timeout=1),
        ]

        if animate:
            # TODO choose right implementation once completed
            # out_handlers.append(Animate(animator=BaseAnimator()))
            pass
        else:
            out_handlers.append(Print(logger=logger, mapper=lambda x: x.value.round(decimals=2)))

        out_handler = HandlersList(out_handlers)

        handlers = []

        for channel in channels:
            channel_handlers = [
                # TODO choose the right accumulator
                # FixedAccumulator(size=200),
                TimedAccumulator[int](time_in_seconds=1/60),
                ExtractCharacteristics(extractor=extractor),
                out_handler
            ]
            handlers.append(ConditionalHandler(condition=ChannelSelection(channel), child=HandlersList(channel_handlers)))

        self.__executor = FromSourceExecutor(source=source, handler=HandlersList(handlers))

    def create(self) -> Executor:
        return self.__executor
