from typing import ClassVar
import xml.etree.ElementTree as ET
import logging
import re

from lint.data import Message
from lint.processors import RelevanceEstimator, MessageSummarizer, Processor
from lint.configuration import *
from lint.errors import ModelOutputError

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
    class ContextSeparator(XmlConfigurable):
        """
        This inner class exists because the user can decide whether
        to split context based on a sequence of characters or a regular expression.
        """

        logger = logging.getLogger(__name__)
        ATTRIB_REGEX = "regex"

        def __init__(self, separator: str | re.Pattern):
            self.separator: str | re.Pattern = separator

        def split(self, response: str) -> tuple[str, str]:
            parts = []
            # Split response based on context separator
            #  (the semantics are different for str and regular expressions)
            if isinstance(self.separator, str):
                parts = response.split(self.separator, maxsplit=2)
            elif isinstance(self.separator, re.Pattern):
                parts = self.separator.split(response, maxsplit=2)
            else:
                raise TypeError(f'Unknown separator type: {type(self.separator)}')

            # Raise an error if the response is malformatted
            if len(parts) < 2:
                raise ModelOutputError(f"Model response contains no context separator: {response}")
            elif not parts[0] or parts[0].isspace():
                # If the first part is empty or blank, try again.
                #   Maybe the output is formatted like
                #       "$$$ 10 $$$ Explanation"
                #   (This has happened during testing.)

                try:
                    return self.split(parts[1])
                except ModelOutputError as err:
                    raise ModelOutputError(f"Model response contains no valid between separators: {response}", err)
            else:
                return tuple(parts)

        #override
        @classmethod
        def get_xml_tag(cls) -> str:
            return "context-separator"
        
        #override
        @classmethod
        def from_xml(cls, node: ET.Element) -> Self:
            # Default value of "regex" is False, so if it is absent, don't use regular expressions
            if cls.ATTRIB_REGEX in node.attrib and text_to_bool(node.attrib[cls.ATTRIB_REGEX]):
                # Use regular expressions
                cls.logger.debug(f"Compiling regular expression: {node.text}")
                
                pattern = re.compile(node.text)                

                cls.logger.debug(f"Compiled Pattern: {pattern}")
                
                return LmBasedRelevanceEstimator.ContextSeparator(pattern)
            else:
                # Use simple character sequences
                return LmBasedRelevanceEstimator.ContextSeparator(node.text)


    logger = logging.getLogger(__name__)

    def __init__(self, model: LanguageModel, relevance_prompt: str, context_separator: ContextSeparator):
        self.model: LanguageModel = model
        self.relevance_prompt: Prompt = relevance_prompt
        self.context_separator: ContextSeparator = context_separator
    
    def estimate_relevance(self, topic: str, message: Message) -> tuple[int, str]:
        response = self.model.query(
            "\n\n".join((
                self.relevance_prompt.with_topic(topic),
                message.title, message.description
                )))
        
        # Split response based on the context separator
        # (and raise an error if the response is malformatted)
        parts = self.context_separator.split(response)

        try:
            score = int(parts[0])
            context = parts[1]

            return score, context
        except ValueError as err:
            logger.error(f"Bad response: {response}")
            raise ModelOutputError(f"Model response score is not an integer: {parts[0]}", err)

    #override
    def get_prompt(self, topic: str):
        return self.relevance_prompt.with_topic(topic)
    
    #override
    def get_config_notice(self) -> str:
        return f"{super().get_config_notice()}:{self.model.get_type()}"

    @classmethod
    def get_type(cls) -> str:
        return _LM_BASED

    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        # Try and get the model
        return LmBasedRelevanceEstimator(
            model = instantiate_type_from_xml(find_single(node, LanguageModel.get_xml_tag()), LanguageModel.available_types),
            relevance_prompt = Prompt.from_xml(find_single(node, Prompt.get_xml_tag())),
            context_separator = LmBasedRelevanceEstimator.ContextSeparator.from_xml(find_single(node, LmBasedRelevanceEstimator.ContextSeparator.get_xml_tag()))
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
    
    #override
    def get_config_notice(self) -> str:
        return f"{super().get_config_notice()}:({self.head_model.get_config_notice()} | {self.body_model.get_config_notice()})"

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
