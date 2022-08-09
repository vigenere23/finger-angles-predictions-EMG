from typing import TypeVar

from modupipe.base import Condition

from src.pipeline.data import ProcessedData

T = TypeVar("T")


class ChannelSelection(Condition[ProcessedData[T]]):
    def __init__(self, channel: int) -> None:
        self.channel = channel

    def check(self, item: ProcessedData[T]) -> bool:
        return item.channel == self.channel
