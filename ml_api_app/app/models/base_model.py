from abc import ABC, abstractmethod
import os
from anthropic import Anthropic
from transformers import pipeline
from openai import OpenAI
from ml_api_app.config.config import Config

class Model(ABC):
    @abstractmethod
    def predict(self, data):
        pass

class OpenAIModel(Model):
    def __init__(self, model_name, temperature, max_tokens):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def predict(self, data):
        chat_completion = self.client.chat.completions.create(
            messages=data["conversation_history"],
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return chat_completion.choices[0].message.content.strip()

class AnthropicModel(Model):
    def __init__(self, model_name, temperature, max_tokens):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    def predict(self, data):
        response = self.client.completions.create(
            model=self.model_name,
            prompt="\n\n".join([f"{m['role']}: {m['content']}" for m in data["conversation_history"]]),
            max_tokens_to_sample=self.max_tokens,
            temperature=self.temperature,
        )
        return response.completion

class HuggingFaceModel(Model):
    def __init__(self, model_name, temperature, max_length):
        self.model = pipeline("text-generation", model=model_name)
        self.temperature = temperature
        self.max_length = max_length

    def predict(self, data):
        prompt = "\n".join([f"{m['role']}: {m['content']}" for m in data["conversation_history"]])
        response = self.model(prompt, max_length=self.max_length, temperature=self.temperature)
        return response[0]['generated_text']

class ModelFactory:
    @staticmethod
    def create_model(provider, strength):
        config = Config.AI_PROVIDERS[provider]
        model_name = config[f"{strength}_model"]
        temperature = config["temperature"]
        max_tokens = config.get("max_tokens") or config.get("max_length")

        if provider == "openai":
            return OpenAIModel(model_name, temperature, max_tokens)
        elif provider == "anthropic":
            return AnthropicModel(model_name, temperature, max_tokens)
        elif provider == "huggingface":
            return HuggingFaceModel(model_name, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
