from abc import ABC, abstractmethod
import os
from typing import Dict, Any, List
from anthropic import Anthropic
from transformers import pipeline
from openai import OpenAI
from config.config import Config
import base64


class Model(ABC):
    @abstractmethod
    def predict(self, data: Dict[str, Any]) -> str:
        pass


class OpenAIModel(Model):
    def __init__(self, model_name: str, **kwargs):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = model_name
        self.kwargs = kwargs

    def predict(self, data: Dict[str, Any]) -> str:
        messages = self._prepare_messages(data)
        
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            **self.kwargs
        )
        return chat_completion.choices[0].message.content.strip()

    def _prepare_messages(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        messages = []
        
        if "conversation_history" in data:
            messages.extend(data["conversation_history"])
        
        if "prompt" in data:
            messages.append({"role": "user", "content": data["prompt"]})
        
        if "html" in data:
            messages.append({"role": "user", "content": f"HTML content:\n{data['html']}"})
        
        if "screenshot" in data:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Here's a screenshot of the current page:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data['screenshot']}"}}
                ]
            })
        
        if "current_step" in data:
            messages.append({"role": "user", "content": f"Current step: {data['current_step']}"})
        
        return messages


class AnthropicModel(Model):
    def __init__(self, model_name: str, **kwargs):
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model_name = model_name
        self.kwargs = kwargs

    def predict(self, data: Dict[str, Any]) -> str:
        prompt = self._prepare_prompt(data)
        
        response = self.client.completions.create(
            model=self.model_name,
            prompt=prompt,
            **self.kwargs
        )
        return response.completion

    def _prepare_prompt(self, data: Dict[str, Any]) -> str:
        prompt_parts = []
        
        if "conversation_history" in data:
            prompt_parts.extend([f"{m['role']}: {m['content']}" for m in data["conversation_history"]])
        
        if "prompt" in data:
            prompt_parts.append(f"Human: {data['prompt']}")
        
        if "html" in data:
            prompt_parts.append(f"Human: HTML content:\n{data['html']}")
        
        if "screenshot" in data:
            prompt_parts.append(f"Human: Here's a screenshot of the current page: [base64 encoded image data]")
        
        if "current_step" in data:
            prompt_parts.append(f"Human: Current step: {data['current_step']}")
        
        return "\n\n".join(prompt_parts)


class HuggingFaceModel(Model):
    def __init__(self, model_name: str, **kwargs):
        self.model = pipeline("text-generation", model=model_name)
        self.kwargs = kwargs

    def predict(self, data: Dict[str, Any]) -> str:
        prompt = self._prepare_prompt(data)
        response = self.model(prompt, **self.kwargs)
        return response[0]['generated_text']

    def _prepare_prompt(self, data: Dict[str, Any]) -> str:
        prompt_parts = []
        
        if "conversation_history" in data:
            prompt_parts.extend([f"{m['role']}: {m['content']}" for m in data["conversation_history"]])
        
        if "prompt" in data:
            prompt_parts.append(f"User: {data['prompt']}")
        
        if "html" in data:
            prompt_parts.append(f"User: HTML content:\n{data['html']}")
        
        if "screenshot" in data:
            prompt_parts.append(f"User: Here's a screenshot of the current page: [base64 encoded image data]")
        
        if "current_step" in data:
            prompt_parts.append(f"User: Current step: {data['current_step']}")
        
        return "\n".join(prompt_parts)


class ModelFactory:
    @staticmethod
    def create_model(provider: str, strength: str) -> Model:
        if provider not in Config.AI_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        config = Config.AI_PROVIDERS[provider]
        strength_key = f"{strength}_model"
        if strength_key not in config:
            raise ValueError(f"Unsupported strength '{strength}' for provider '{provider}'")

        model_name = config[strength_key]
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
