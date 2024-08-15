## instalation guide: https://huggingface.co/docs/transformers/main/installation
## source test_llm.env/bin/activate

## install Nvidia driver, install cuda, install pytorch, install mixtral


from transformers import pipeline

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]
chatbot = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.3")
chatbot(messages)
