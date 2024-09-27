from typing import ClassVar
import xml.etree.ElementTree as ET
import logging

from lint.data import Message
from lint.processors import RelevanceEstimator, MessageSummarizer, Processor
from lint.configuration import *

_LM_BASED = "lm-based"

@dataclass
class Prompt(XmlConfigurable):
    parts: list[str]

    def with_topic(self, description: str):
        return description.join(self.parts)

    @classmethod
    def get_xml_tag(cls) -> str:
        return "prompt"
    
    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Inner text is broken up by tags
        return Prompt(parts = list(node.itertext()))

class LanguageModel(Processor):
    logger = logging.getLogger(__name__)

    available_types: ClassVar[list[type]] = []

    def __init__(self, properties: dict[str, str]):
        pass

    def query(self, content: str) -> str:
        raise NotImplementedError("query() has not been implemented")
    
    #override
    @classmethod
    def get_xml_tag(cls) -> str:
        return "model"
    
    @classmethod
    def _properties_from_xml(cls, node: ET.ElementTree) -> dict[str, str]:
        # Read properties
        properties = dict([(get_attrib_or_err(prop, "key"), prop.text) for prop in node.findall("property")])
        cls.logger.debug(f"Read {len(properties)} properties from model of type '{node.attrib['type']}'")
        
        return properties

class LmBasedRelevanceEstimator(RelevanceEstimator):

    def __init__(self, model: LanguageModel, relevance_prompt: str, context_separator: str):
        self.model: LanguageModel = model
        self.relevance_prompt: Prompt = relevance_prompt
        self.context_separator: str = context_separator
    
    def estimate_relevance(self, topic: str, message: Message) -> tuple[int, str]:
        # TODO Process response instead of raising an error!
        # self.model.query("\n\n".join((self.relevance_prompt, message.title, message.description)))
        raise NotImplementedError()
    
    #override
    def get_prompt(self, topic: str):
        return self.relevance_prompt.with_topic(topic)
    
    @classmethod
    def get_type(cls) -> str:
        return _LM_BASED

    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Try and get the model
        return LmBasedRelevanceEstimator(
            model = instantiate_type_from_xml(find_single(node, LanguageModel.get_xml_tag()), LanguageModel.available_types),
            relevance_prompt = Prompt.from_xml(find_single(node, Prompt.get_xml_tag())),
            context_separator = find_single(node, "context-separator").text
        )

class LmBasedMessageSummarizer(MessageSummarizer):
    body_model: LanguageModel
    body_prompt: Prompt

    head_model: LanguageModel
    head_prompt: Prompt

    def __init__(self, body_model: LanguageModel, body_prompt: str, head_model: LanguageModel, head_prompt: str):
        self.body_model = body_model
        self.body_prompt = body_prompt

        self.head_model = head_model
        self.head_prompt = head_prompt
    
    @staticmethod
    def _combine_msg_prompt(prompt: str, messages: tuple[Message, ...]) -> str:
        return "\n\n".join([prompt] +
            ['\n\n'.join(("### start article ###", message.title, message.description, "### end article ###"))
                for message in messages])

    def summarize(self, topic: str, cluster: tuple[Message, ...]) -> tuple[str, str]:
        # TODO Is this way of combining messages good?
        prompt_combine_messages = LmBasedMessageSummarizer._combine_msg_prompt(self.body_prompt.with_topic(topic), cluster)
        summary = self.body_model.query(prompt_combine_messages)

        # The title is generated from the summary in a second pass,
        # so that it is consistent with the summary
        # (the two steps are dependent on each other)
        title = self.head_model.query("\n\n".join(head_prompt.with_topic(topic), summary))

        return (title, summary)
    
    #override
    def get_prompt(self, topic: str):
        return self.body_prompt.with_topic(topic)
    
    @classmethod
    def get_type(cls) -> str:
        return _LM_BASED

    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Interpret for head and body
        head_node = find_single(node, "head")
        body_node = find_single(node, "body")

        def instantiate_model(node: ET.Element):
            return instantiate_type_from_xml(find_single(node, LanguageModel.get_xml_tag()), LanguageModel.available_types)
        def get_prompt(node: ET.Element):
            return Prompt.from_xml(find_single(node, Prompt.get_xml_tag()))

        return LmBasedMessageSummarizer(
            body_model = instantiate_model(body_node),
            body_prompt = get_prompt(body_node),

            head_model = instantiate_model(head_node),
            head_prompt = get_prompt(head_node)
        )
