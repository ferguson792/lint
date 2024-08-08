from enum import Enum
from typing import Optional, Self
from dataclasses import dataclass
from datetime import datetime

SourceId = int
ItemId = int
ClassificationLevels = tuple[str, ...]

class SourceType(Enum):
    RSS = 1

class SourceStatus(Enum):
    LIVE = 1

@dataclass
class QuarantineStatus:
    sql_injection_detected: bool
    lm_injection_detected: bool

    def from_int(status: int) -> Self:
        return QuarantineStatus(status & 0b10, status & 0b01)

    def to_int(self):
        return (0b10 if sql_injection_detected else 0) | (0b01 if lm_injection_detected else 0)

class Source:
    uid: Optional[SourceId]
    uri: str
    classification: ClassificationLevels
    type: SourceType
    status: SourceStatus

    def __init__(self, uid: SourceId, uri: str):
        self.uid = uid
        self.uri = uri
        self.classification = ("PUBLIC",)
        self.type = SourceType.RSS
        self.status = SourceStatus.LIVE

@dataclass
class Item:
    """
    An Item is the object received from the source it. It contains all the metadata
    as well as the unprocessed, i.e. raw, message content.
    """
    uid: Optional[ItemId]
    link: str
    guid: Optional[str]
    pub_date: Optional[str]
    raw_item: str

    source_uid: SourceId
    access_date: datetime
    classification: ClassificationLevels
    quarantine_status: QuarantineStatus
