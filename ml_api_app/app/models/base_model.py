from abc import ABC, abstractmethod
import os
from anthropic import Anthropic
# from deepseek import DeepSeek
from transformers import pipeline


class Model(ABC):
    @abstractmethod
    def predict(self, data):
        pass


class OpenAIModel(Model):
    def __init__(self, api_key):
        import os
        from openai import OpenAI

        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def predict(self, data):
        chat_completion = self.client.chat.completions.create(
            messages=data["conversation_history"],
            model="gpt-4",
        )

        response = chat_completion.choices[0].message.content.strip()
        return response


class AnthropicModel(Model):
    def __init__(self, api_key):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def predict(self, data):
        response = self.client.completions.create(
            model="claude-2",
            prompt="\n\n".join(
                [f"{m['role']}: {m['content']}" for m in data["conversation_history"]]),
            max_tokens_to_sample=1000
        )
        return response.completion


""" 
class DeepSeekModel(Model):
    def __init__(self, api_key):
        self.client = DeepSeek(api_key=os.environ.get("DEEPSEEK_API_KEY"))

    def predict(self, data):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=data["conversation_history"]
        )
        return response.choices[0].message.content """


class WeakModel(Model):
    def __init__(self, model_type):
        if model_type == "openai":
            self.model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
        elif model_type == "huggingface":
            self.model = pipeline("text-generation", model="phi-3-mini")
        elif model_type == "anthropic":
            self.model = AnthropicModel(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # elif model_type == "deepseek":
        #     self.model = DeepSeekModel(api_key=os.getenv("DEEPSEEK_API_KEY"))
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def predict(self, data):
        return self.model.predict(data)


class StrongModel(Model):
    def __init__(self, model_type):
        if model_type == "openai":
            self.model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
        elif model_type == "huggingface":
            self.model = pipeline("text-generation", model="Llama3-70b")
        elif model_type == "anthropic":
            self.model = AnthropicModel(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # elif model_type == "deepseek":
        #    self.model = DeepSeekModel(api_key=os.getenv("DEEPSEEK_API_KEY"))
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def predict(self, data):
        return self.model.predict(data)
