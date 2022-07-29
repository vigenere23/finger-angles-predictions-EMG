from modupipe.sink import Sink

from src.pipeline.data import ProcessedData


class ChannelSelection(Sink[ProcessedData]):
    def __init__(self, channel: int, sink: Sink[ProcessedData]) -> None:
        self.channel = channel
        self.sink = sink

    def receive(self, item: ProcessedData) -> None:
        if item.channel == self.channel:
            self.sink.receive(item)
