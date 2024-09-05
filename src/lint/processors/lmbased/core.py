from lint.data import Message
from lint.processors import RelevanceEstimator, MessageSummarizer

class LanguageModel:
    def query(self, content: str) -> str:
        raise NotImplementedError("query() has not been implemented")

class LmBasedRelevanceEstimator(RelevanceEstimator):
    model: LanguageModel
    relevance_prompt: str

    def __init_(self, model: MistralModelClient, relevance_prompt: str):
        self.model = model
        self.relevance_prompt = relevance_prompt
    
    def estimate_relevance(self, message: Message) -> tuple[int, str]:
        self.model.query("\n\n".join((self.relevance_prompt, message.title, message.description)))

class LmBasedMessageSummarizer(MessageSummarizer):
    model: LanguageModel
    summary_prompt: str
    title_prompt: str

    def __init__(self, model: MistralModelClient, summary_prompt: str):
        self.model = model
        self.summary_prompt = summary_prompt
    
    def summarize(self, cluster: tuple[Message, ...]) -> tuple[str, str]:
        # TODO Is this way of combining messages good?
        prompt_combine_messages = "\n\n".join(
            [self.summary_prompt] +
            ['\n\n'.join(("### start article ###", message.title, message.description, "### end article ###"))
                for message in cluster]
            )
        summary = self.model.query(prompt_combine_messages)
        # The title is generated from the summary in a second pass,
        # so that it is consistent with the summary
        # (the two steps are dependent on each other)
        title = self.model.query("\n\n".join(title_prompt, summary))
        return (
            title,
            summary
            )
