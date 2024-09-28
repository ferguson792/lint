from enum import IntEnum
from typing import Optional, Self
from dataclasses import dataclass
from datetime import datetime

from lint.harmonization import Harmonizable, Harmonizer

SourceId = int
ItemId = int
MessageId = int
BriefId = int
SummaryId = int
ClassificationLevels = tuple[str, ...]
# The cluster number is explicitly NOT an id, because the same number can refer
# to different clusters depending on the generation batch number
ClusterNumber = int

# TODO Simplify to RSS_ATOM
class SourceType(IntEnum):
    RSS = 1
    ATOM = 2

class SourceStatus(IntEnum):
    UNKNOWN = 1
    LIVE = 2
    DEAD = 3

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

class TopicVector:
    value: tuple[float, ...]

@dataclass
class Source(Harmonizable):
    uid: Optional[SourceId]
    uri: str
    classification: ClassificationLevels
    type: SourceType
    status: SourceStatus

@dataclass
class Item(Harmonizable):
    """
    An Item is the object received from the source it. It contains all the metadata
    as well as the unprocessed, i.e. raw, message content.
    """
    uid: Optional[ItemId]
    link: Optional[str]
    guid: Optional[str]
    pub_date: Optional[str]
    raw_item: str

    source: Source
    access_date: datetime                   # TODO Might be better to rename this in "first_received_date", and use a POSIX timestamp?
    classification: ClassificationLevels
    quarantine_status: QuarantineStatus
    processing_status: ProcessingStatus

@dataclass
class Message:
    uid: Optional[MessageId]
    item: Item
    title: str
    description: str
    relevance: Optional[int]
    relevance_context: Optional[str]  # Explicitly not '_explanation', because we can't describe the LLM's output as an "explanation";
                                      # that would be incorrectly assuming meaning from form
    topic_vector: Optional[TopicVector]
    cluster: Optional[ClusterNumber]

    def text(self) -> str:
        """
        Returns the title and description of the Message,
        separated by two line breaks.
        This method exists because this operation is used quite often
        during processing.
        """
        return "\n\n".join((self.title, self.description))

@dataclass
class Brief:
    uid: Optional[BriefId]
    cutoff_date: datetime                   # Cutoff date, stored as datetime
    viewback_ms: int                        # Viewback timespan in milliseconds
    classification: ClassificationLevels    # Classification levels will probably be stored in their own table...
    topic_descriptions: str                 # The Brief's focus (topic descriptions)
    num_clusters: int                       # Number of clusters
    config_notice: str                      # The configuration notice      # TODO Include more and more granular metadata

    # TODO Create a helper method to create from briefing parameters?


@dataclass
class Summary:
    uid: Optional[SummaryId]
    brief: Brief
    generation_date: int    # A POSIX timestamp
    title: str
    summary: str
    cluster: ClusterNumber
    classification: ClassificationLevels
    source_items: tuple[Item, ...]
    issued: bool
