from abc import ABC, abstractmethod
import os


class Model(ABC):
    @abstractmethod
    def predict(self, data):
        pass


class OpenAIModel(Model):
    def __init__(self, api_key):
        import os
        from openai import OpenAI

        self.conversation_history = []
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def predict(self, data):
        self.conversation_history.append(
            {"role": "user", "content": data["prompt"]})

        chat_completion = self.client.chat.completions.create(
            messages=self.conversation_history,
            model="gpt-4",
        )

        response = chat_completion.choices[0].message.content.strip()
        self.conversation_history.append(
            {"role": "assistant", "content": response})

        return response


class WeakModel(Model):
    def __init__(self, model_type):
        if model_type == "openai":
            self.model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
        elif model_type == "huggingface":
            from transformers import pipeline
            self.model = pipeline("text-generation", model="phi-3-mini")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def predict(self, data):
        return self.model.predict(data)


class StrongModel(Model):
    def __init__(self, model_type):
        if model_type == "openai":
            self.model = OpenAIModel(api_key=os.getenv("OPENAI_API_KEY"))
        elif model_type == "huggingface":
            from transformers import pipeline
            self.model = pipeline("text-generation", model="Llama3-70b")
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def predict(self, data):
        return self.model.predict(data)
