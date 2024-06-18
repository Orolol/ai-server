from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def predict(self, data):
        pass

class OpenAIModel(Model):
    def __init__(self, api_key):
        import openai
        self.api_key = api_key
        openai.api_key = self.api_key

    def predict(self, data):
        response = openai.Completion.create(
            engine="davinci",
            prompt=data["prompt"],
            max_tokens=50
        )
        return response.choices[0].text.strip()

class HuggingFaceModel(Model):
    def __init__(self, model_name):
        from transformers import pipeline
        self.model = pipeline("text-generation", model=model_name)

    def predict(self, data):
        return self.model(data["prompt"])[0]["generated_text"]
