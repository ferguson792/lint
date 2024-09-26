from typing import Self
import logging
import xml.etree.ElementTree as ET

from lint.processors.lmbased import LanguageModel

from mistralai import Mistral

# TODO It should be possible to load models from a file with a simple XML format
class MistralClientModel(LanguageModel):
    logger = logging.getLogger(__name__)


    def __init__(self, properties: dict[str, str]):
        self.model_name: str = properties['name']
        
        # Try and convert the given temperature to a floating point number
        temperature_str = properties['temperature']
        try:
            self.temperature: float = float(temperature_str)
        except TypeError as err:
            raise ValueError(f"Temperature is not of type 'str': {temperature_str}")
        except ValueError as err:
            raise ValueError(f"Temperature is not a floating point number: {temperature_str}", err)
        
        # Initiate the Mistral client with the given key and token
        api_key = properties['auth-token']
        self.client = Mistral(api_key=api_key)

    def query(self, content: str) -> str:
        chat_response = self.client.chat.complete(
            model=self.model_name,
            temperature=self.temperature,
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return chat_response.choices[0].message.content

    #override
    @classmethod
    def get_type(cls) -> str:
        return "mistral-online"
    
    #override
    @classmethod
    def from_xml(cls, node: ET.Element) -> Self:
        return MistralClientModel(properties=cls._properties_from_xml(node))
