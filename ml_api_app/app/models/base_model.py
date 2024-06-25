from abc import ABC, abstractmethod
import os
from anthropic import Anthropic
from transformers import pipeline
from openai import OpenAI
from config.config import Config


class Model(ABC):
    @abstractmethod
    def predict(self, data):
        pass


class OpenAIModel(Model):
    def __init__(self, model_name, **kwargs):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.kwargs = kwargs

    def predict(self, data):
        chat_completion = self.client.chat.completions.create(
            messages=data["conversation_history"],
            model=self.model_name,
            **self.kwargs
        )
        return chat_completion.choices[0].message.content.strip()


class AnthropicModel(Model):
    def __init__(self, model_name, **kwargs):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model_name = model_name
        self.kwargs = kwargs

    def predict(self, data):
        response = self.client.completions.create(
            model=self.model_name,
            prompt="\n\n".join(
                [f"{m['role']}: {m['content']}" for m in data["conversation_history"]]),
            **self.kwargs
        )
        return response.completion


class HuggingFaceModel(Model):
    def __init__(self, model_name, **kwargs):
        self.model = pipeline("text-generation", model=model_name)
        self.kwargs = kwargs

    def predict(self, data):
        prompt = "\n".join(
            [f"{m['role']}: {m['content']}" for m in data["conversation_history"]])
        response = self.model(prompt, **self.kwargs)
        return response[0]['generated_text']


class ModelFactory:
    @staticmethod
    def create_model(provider, strength):
        config = Config.AI_PROVIDERS[provider]
        model_name = config[f"{strength}_model"]
        model_params = {k: v for k, v in config.items() if k not in [
            "weak_model", "strong_model"]}

        if provider == "openai":
            return OpenAIModel(model_name, **model_params)
        elif provider == "anthropic":
            return AnthropicModel(model_name, **model_params)
        elif provider == "huggingface":
            return HuggingFaceModel(model_name, **model_params)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
