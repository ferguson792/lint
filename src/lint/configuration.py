from abc import ABC, abstractmethod
from typing import Self, Optional, Any
from dataclasses import dataclass

import xml.etree.ElementTree as ET

from lint.errors import ConfigurationError

# This magic constant is used in multiple other modules
TYPE_ATTRIB = "type"

class XmlConfigurable(ABC):
    """
    The abstract base class (ABC) for all elements which are configurable via XML.
    """
    @classmethod
    @abstractmethod
    def from_xml(cls, element: ET.Element) -> Self:
        pass
    
    @classmethod
    @abstractmethod
    def get_xml_tag(cls) -> str:
        pass

@dataclass
class Topic(XmlConfigurable):
    description: str
    relevance_threshold: int

    @classmethod
    def get_xml_tag(cls) -> str:
        return "topic"

    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Should have exactly two sub-nodes: description and relevance-threshold
        try:
            return Topic(
                description=get_attrib_or_err(node, "description"),
                relevance_threshold=int(get_attrib_or_err(node, "relevance-threshold"))
            )
        except ValueError as err:
            raise ConfigurationError(err)

@dataclass
class BriefingParameters(XmlConfigurable):
    viewback_ms: int
    ignore_pub_date: bool
    ignore_processing_status: bool

    join_with: str

    topics: list[Topic]

    def join_topics_for_prompt(self) -> str:
        return self.join_with.join([topic.description for topic in self.topics])
    
    def topics_to_str(self) -> str:
        return " / ".join([topic.description for topic in self.topics])

    @classmethod
    def get_xml_tag(cls) -> str:
        return "parameters"

    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Should have exactly four sub-nodes: viewback-ms, ignore-publication-date, ignore-processing-status, topics
        try:
            topics_node = find_single(node, "topics")
            topics = [Topic.from_xml(topic_node) for topic_node in topics_node]

            return BriefingParameters(
                viewback_ms = int(find_single(node, 'viewback-ms').text),
                ignore_pub_date = text_to_bool(find_single(node, "ignore-publication-date").text),
                ignore_processing_status = text_to_bool(find_single(node, "ignore-processing-status").text),
                join_with = get_attrib_or_err(topics_node, "join-with"),
                topics = topics
            )
        except ValueError as err:
            raise ConfigurationError(err)


### UTILITY FUNCTIONS ###

def find_single(node: ET.Element, tag: str, must_exist: bool=True) -> Optional[ET.Element]:
    elements = node.findall(f"./{tag}")
    if len(elements) < 1 and must_exist:
        raise ConfigurationError(f"Missing tag <{tag}> in <{node.tag}>")
    if len(elements) > 1:
        raise ConfigurationError(f"Tag <{tag}> is defined more than once")
    
    return elements[0]

def get_attrib_or_err(node: ET.Element, attrib: str) -> Any:
    try:
        return node.attrib[attrib]
    except KeyError as err:
        raise ConfigurationError(f"Missing attribute '{attrib}' on element <{node.tag}>", err)

def instantiate_type_from_xml(node: ET.Element, available_types: list):
    # Select a type based on the available (registered) types
    type_attrib = get_attrib_or_err(node, TYPE_ATTRIB)

    for available_type in available_types:
        if available_type.get_type() == type_attrib:
            return available_type.from_xml(node)
    
    # If no object with the type could be found, raise an error
    raise ConfigurationError(f'Unknown {node.tag} type: "{type_attrib}"')

_TRUE_VALUES = ("true", "yes")
_FALSE_VALUES = ("false", "no")

def text_to_bool(value: str) -> bool:
    if value in _TRUE_VALUES:
        return True
    elif value in _FALSE_VALUES:
        return False
    else:
        raise ValueError(f"Unknown boolean value: {value}. Must be either {'/'.join(_TRUE_VALUES)} or {'/'.join(_FALSE_VALUES)}")
