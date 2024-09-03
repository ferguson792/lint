from lint.processors import *

# Dummy processors, to be used for testing

class DummyMaliciousDetector(MaliciousDetector):
    """
    This detector always returns False and should never be used in production.
    """
    def is_malicious_text(self, text: str) -> bool:
        return False

class DummyRelevanceEstimator(RelevanceEstimator):
    """
    This dummy estimator estimates everything as very relevant (100).
    """
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        return 100, "dummy"

class DummyMessageSummarizer(MessageSummarizer):
    """
    This dummy summarizer just pulls the first word from each title,
    and the first word from each description, to generate the summary.
    """
    def summarize(self, cluster: tuple[Message, ...]) -> tuple[str, str]:
        title_parts = []
        content_parts = []
        for message in cluster:
            title_parts.append(message.title.split(' ', maxsplit=1)[0])
            content_parts.append(message.description.split(' ', maxsplit=1)[0])

        return (" ".join(title_parts), " ".join(content_parts))
