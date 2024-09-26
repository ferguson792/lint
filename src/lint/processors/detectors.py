import xml.etree.ElementTree as ET

from lint.processors import MaliciousDetector
from lint.configuration import *

class BlackListDetector(MaliciousDetector):
    blacklist: set[str]

    def __init__(self, blacklist: list[str]):
        # PREPROCESSING:
        # - Convert to lowercase
        # - Remove duplicates (convert to set)
        self.blacklist = set([element.lower() for element in blacklist])
    
    @classmethod
    def from_file(cls, path: str) -> Self:
        with open(path, "r+") as file:
            return BlackListDetector(file.readlines())
    
    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # This node should have exactly one sub-node: list
        list_node = find_single(node, "list")
        ref_attrib = get_attrib_or_err(list_node, "ref")

        return BlackListDetector.from_file(ref_attrib)

    #override
    def is_malicious_text(self, text: str) -> bool:
        # Make text lowercase and normalize whitespaceing (split and join again)
        text_processed = ' '.join(text.lower().split())
        
        for element in self.blacklist:
            if element in text_processed:
                return True
        
        return False

# TODO Regex matching
