from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

DataType = TypeVar('DataType')

@dataclass
class SourceData(Generic[DataType]):
    value: DataType
    start: datetime
    end: datetime
    nb_channels: int
    length: int
    message_length: int


@dataclass
class ProcessedData(Generic[DataType]):
    time: float
    channel: int
    original: DataType
    filtered: DataType


@dataclass
class RangeData(Generic[DataType]):
    start: float
    end: float
    value: DataType
