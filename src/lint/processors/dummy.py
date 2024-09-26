from xml.etree.ElementTree import Element

from lint.processors.interface import *

# Dummy processors, to be used for testing

class DummyMaliciousDetector(MaliciousDetector):
    """
    This detector always returns False and should never be used in production.
    """

    def is_malicious_text(self, text: str) -> bool:
        return False
    
    #override
    @classmethod
    def get_type(cls) -> str:
        return "dummy"
    
    #override
    @classmethod
    def from_xml(cls, node: Element) -> Self:
        return DummyMaliciousDetector()

class DummyRelevanceEstimator(RelevanceEstimator):
    """
    This dummy estimator estimates everything as very relevant (100).
    """

    def estimate_relevance(self, topic: str, message: Message) -> tuple[int, str]:
        return 100, "dummy"
    
    #override
    def get_prompt(self, topic: str) -> str:
        return "DUMMY"

    #override
    @classmethod
    def get_type(cls) -> str:
        return "dummy"
    
    #override
    @classmethod
    def from_xml(cls, node: Element) -> Self:
        return DummyRelevanceEstimator()

class DummyMessageCategorizer(MessageCategorizer):
    """
    This dummy categorizer just returns a single cluster.
    """

    def cluster(self, messages: list[Message]) -> list[tuple[Message, ...]]:
        return [tuple(messages)]
    
    #override
    @classmethod
    def get_type(cls) -> str:
        return "dummy"
    
    #override
    @classmethod
    def from_xml(cls, node: Element) -> Self:
        return DummyMessageCategorizer()

class DummyMessageSummarizer(MessageSummarizer):
    """
    This dummy summarizer just pulls the first word from each title,
    and the first word from each description, to generate the summary.
    """

    def summarize(self, topic: str, cluster: tuple[Message, ...]) -> tuple[str, str]:
        title_parts = []
        content_parts = []
        for message in cluster:
            title_parts.append(message.title.split(' ', maxsplit=1)[0])
            content_parts.append(message.description.split(' ', maxsplit=1)[0])

        return (" ".join(title_parts), " ".join(content_parts))
    
    def get_prompt(self, topic: str):
        return "DUMMY"

    #override
    @classmethod
    def get_type(cls) -> str:
        return "dummy"
    
    #override
    @classmethod
    def from_xml(cls, node: Element) -> Self:
        return DummyMessageSummarizer()
