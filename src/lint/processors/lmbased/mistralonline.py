from lint.processors.lmbased import LanguageModel

from mistralai import Mistral

# TODO It should be possible to load models from a file with a simple XML format
class MistralClientModel(LanguageModel):
    # Temperature for fine-tuning
    model: str
    temperature: float

    client: Mistral

    def __init__(self, model: str, temperature: float, api_key: str):
        self.model = model
        self.temperature = temperature
        self.client = Mistral(api_key=api_key)
    
    def query(self, content: str) -> str:
        chat_response = client.chat.complete(
            model=self.model,
            temperature=self.temperature,
            messages = [
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
        return chat_response.choices[0].message.content
