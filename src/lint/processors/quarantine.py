from lint.configuration import *
from lint.processors import MaliciousDetector
from lint.data import QuarantineStatus

class QuarantineIndicator(XmlConfigurable):
    sql_inj_det: MaliciousDetector
    lm_inj_det: MaliciousDetector

    def __init__(self, sql_inj_det: MaliciousDetector, prompt_inj_det: MaliciousDetector):
        self.sql_inj_det = sql_inj_det
        self.lm_inj_det = prompt_inj_det
    
    def indicate_for_text(self, text: str) -> QuarantineStatus:
        return QuarantineStatus(
            sql_injection_detected=self.sql_inj_det.is_malicious_text(text),
            lm_injection_detected=self.lm_inj_det.is_malicious_text(text)
        )
    
    #override
    @classmethod
    def get_xml_tag(cls) -> str:
        return "quarantine"

    #override
    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # This is a helper function used to extract the detector with the right 'type'
        # from the surrounding context
        def get_detector_from_xml(super_node: ET.Element) -> MaliciousDetector:
            return instantiate_type_from_xml(
                node = find_single(super_node, MaliciousDetector.get_xml_tag()),
                available_types = MaliciousDetector.available_types
            )

        # Get SQL injection and prompt injection detectors:
        # Both should have only a single sub-element: <detector>
        # This detector should have an attribute called 'type',
        # which we can use to construct the appropriate detector:
        return QuarantineIndicator(
            sql_inj_det = get_detector_from_xml(find_single(node, "sql-injection")),
            prompt_inj_det = get_detector_from_xml(find_single(node, "prompt-injection"))
        )
