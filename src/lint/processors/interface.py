from lint.data import Item, QuarantineStatus, Message

class MaliciousDetector:
    """
    This class encapsulates the functionality required to (attempt to) detect malicious messages,
    and is used to detect both Language Model (aka "Prompt") as well as SQL injections in given text.
    """
    def is_malicious_item(self, item: Item) -> bool:
        return self.is_malicious_text(item.raw_item)
    
    def is_malicious_text(self, text: str) -> bool:
        raise NotImplementedError()

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
    """
    The RelevanceEstimator is used to estimate the relevance
    of a given message for a topic.
    """
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        raise NotImplementedError()

class MessageSummarizer:
    """
    The MessageSummarizer is supposed to summarize a cluster of messages.
    """
    def summarize(self, cluster: tuple[Message, ...]) -> tuple[str, str]:
        return NotImplementedError()
