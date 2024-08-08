from lint.data import Item, QuarantineStatus

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
