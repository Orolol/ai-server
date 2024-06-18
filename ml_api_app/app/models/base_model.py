from abc import ABC, abstractmethod

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
            messages=[
                {
                    "role": "user",
                    "content": data["prompt"],
                }
            ],
            model="gpt-4",
        )
        return chat_completion.choices[0].message["content"].strip()

class HuggingFaceModel(Model):
    def __init__(self, model_name):
        from transformers import pipeline
        self.model = pipeline("text-generation", model=model_name)

    def predict(self, data):
        return self.model(data["prompt"])[0]["generated_text"]
