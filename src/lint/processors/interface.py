from typing import Self, ClassVar

from lint.data import Item, QuarantineStatus, Message
from lint.configuration import *

class Processor(XmlConfigurable):
    @classmethod
    def get_type(cls) -> str:
        raise NotImplementedError(f"get_type() not implemented for {cls}")

    #override
    @classmethod
    def get_xml_tag(cls):
        return "processor"

class MaliciousDetector(Processor):
    """
    This class encapsulates the functionality required to (attempt to) detect malicious messages,
    and is used to detect both Language Model (aka "Prompt") as well as SQL injections in given text.
    """
    available_types: ClassVar[list[type]] = []

    def is_malicious_text(self, text: str) -> bool:
        raise NotImplementedError()

    #override
    @classmethod
    def get_xml_tag(cls) -> str:
        return "detector"


class RelevanceEstimator(Processor):
    """
    The RelevanceEstimator is used to estimate the relevance
    of a given message for a topic.
    """
    available_types: ClassVar[list[type]] = []

    def estimate_relevance(self, topic: str, message: Message) -> tuple[int, str]:
        raise NotImplementedError()
    
    def get_prompt(self, topic: str) -> str:
        raise NotImplementedError()


class MessageCategorizer(Processor):
    """
    The MessageCategorizer takes messages and turns them into clusters.
    A message can be in more than one cluster.
    """
    available_types: ClassVar[list[type]] = []

    def cluster(self, messages: list[Message]) -> list[tuple[Message, ...]]:
        raise NotImplementedError()
    
    @classmethod
    def get_xml_tag(cls):
        return "processor"

class MessageSummarizer(Processor):
    """
    The MessageSummarizer is supposed to summarize a cluster of messages.
    """
    available_types: ClassVar[list[type]] = []

    def summarize(self, topic: str, cluster: tuple[Message, ...]) -> tuple[str, str]:
        return NotImplementedError()
    
    def get_prompt(self, topic: str) -> str:
        return NotImplementedError()
