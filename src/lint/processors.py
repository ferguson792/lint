from lint.data import Item, QuarantineStatus, Message

class MaliciousDetector:
    def is_malicious_item(self, item: Item) -> bool:
        return self.is_malicious_text(item.raw_item)
    
    def is_malicious_text(self, text: str) -> bool:
        raise NotImplementedError()

class NeverMaliciousDetector:
    """
    This detector always returns False and should never be used in production.
    """
    def is_malicious_text(self, text: str) -> bool:
        return False

class QuarantineIndicator:
    sql_inj_det: MaliciousDetector
    lm_inj_det: MaliciousDetector

    def __init__(self, sql_inj_det: MaliciousDetector, lm_inj_det: MaliciousDetector):
        self.sql_inj_det = sql_inj_det
        self.lm_inj_det = lm_inj_det
    
    def indicate_for_text(self, text: str) -> QuarantineStatus:
        return QuarantineStatus(
            sql_injection_detected=self.sql_inj_det.is_malicious_text(text),
            lm_injection_detected=self.lm_inj_det.is_malicious_text(text)
        )

class RelevanceEstimator:
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        raise NotImplementedError()

class DummyRelevanceEstimator(RelevanceEstimator):
    """
    This dummy estimator estimates everything as very relevant (100).
    """
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        return 100, "dummy"

class MessageSummarizer:
    def summarize(self, cluster: tuple[Message, ...]) -> tuple[str, str]:
        return NotImplementedError()

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
