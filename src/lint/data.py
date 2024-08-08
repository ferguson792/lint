from enum import IntEnum
from typing import Optional, Self
from dataclasses import dataclass
from datetime import datetime

SourceId = int
ItemId = int
ClassificationLevels = tuple[str, ...]

class SourceType(IntEnum):
    RSS = 1

class SourceStatus(IntEnum):
    LIVE = 1

class ProcessingStatus(IntEnum):
    UN_PROCESSED = 0
    PRE_PROCESSED = 1
    FULLY_PROCESSED = 2

@dataclass
class QuarantineStatus:
    sql_injection_detected: bool
    lm_injection_detected: bool

    def from_int(status: int) -> Self:
        return QuarantineStatus(status & 0b10, status & 0b01)

    def to_int(self):
        return (0b10 if self.sql_injection_detected else 0) | (0b01 if self.lm_injection_detected else 0)

@dataclass
class Source:
    uid: Optional[SourceId]
    uri: str
    classification: ClassificationLevels
    type: SourceType
    status: SourceStatus

@dataclass
class Item:
    """
    An Item is the object received from the source it. It contains all the metadata
    as well as the unprocessed, i.e. raw, message content.
    """
    uid: Optional[ItemId]
    link: Optional[str]
    guid: Optional[str]
    pub_date: Optional[str]
    raw_item: str

    source_uid: SourceId
    access_date: datetime                   # TODO Might be better to rename this in "first_received_date"
    classification: ClassificationLevels
    quarantine_status: QuarantineStatus
    processing_status: ProcessingStatus
