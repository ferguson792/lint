from lint.data import Message
from lint.processors import RelevanceEstimator, MessageSummarizer
from lint.configuration import LanguageModelConfiguration

class LanguageModel:
    def __init__(self, config: LanguageModelConfiguration):
        pass

    def query(self, content: str) -> str:
        raise NotImplementedError("query() has not been implemented")

class LmBasedRelevanceEstimator(RelevanceEstimator):
    model: LanguageModel
    relevance_prompt: str

    def __init__(self, model: LanguageModel, relevance_prompt: str):
        self.model = model
        self.relevance_prompt = relevance_prompt
    
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        # TODO Process response!
        self.model.query("\n\n".join((self.relevance_prompt, message.title, message.description)))

class LmBasedMessageSummarizer(MessageSummarizer):
    body_model: LanguageModel
    body_prompt: str

    head_model: LanguageModel
    head_prompt: str

    def __init__(self, body_model: LanguageModel, body_prompt: str, head_model: LanguageModel, head_prompt: str):
        self.body_model = body_model
        self.body_prompt = body_prompt

        self.head_model = head_model
        self.head_prompt = head_prompt
    
    def _combine_msg_prompt(prompt: str, messages: tuple[Message, ...]) -> str:
        return "\n\n".join(
            [prompt] +
            ['\n\n'.join(("### start article ###", message.title, message.description, "### end article ###"))
                for message in messages]
        )

    def summarize(self, cluster: tuple[Message, ...]) -> tuple[str, str]:
        # TODO Is this way of combining messages good?
        prompt_combine_messages = _combine_msg_prompt(self.body_prompt, cluster)
        summary = self.body_model.query(prompt_combine_messages)
        # The title is generated from the summary in a second pass,
        # so that it is consistent with the summary
        # (the two steps are dependent on each other)
        title = self.head_model.query("\n\n".join(head_prompt, summary))
        return (
            title,
            summary
            )
