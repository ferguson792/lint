import logging

from lint.processors.lmbased import LanguageModel
from lint.configuration import LanguageModelConfiguration

from mistralai import Mistral

# TODO It should be possible to load models from a file with a simple XML format
class MistralClientModel(LanguageModel):
    logger = logging.getLogger(__name__)

    model_name: str
    temperature: float  # Temperature for fine-tuning

    client: Mistral

    def __init__(self, config: LanguageModelConfiguration):
        self.model_name = config.properties['name']
        
        # Try and convert the given temperature to a floating point number
        temperature_str = config.propertes['temperature']
        try:
            self.temperature = float(temperature_str)
        except ValueError:
            raise ValueError(f"Temperature is not a floating point number: {temperature_str}")
        
        # Initiate the Mistral client with the given key and token
        api_key = config.properties['auth-token']
        self.client = Mistral(api_key=api_key)

    def query(self, content: str) -> str:
        chat_response = client.chat.complete(
            model_name=self.model_name,
            temperature=self.temperature,
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return chat_response.choices[0].message.content
