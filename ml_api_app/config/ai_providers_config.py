from typing import Dict, Any

ai_providers_config: Dict[str, Dict[str, Any]] = {
    "openai": {
        "weak_model": "gpt-3.5-turbo",
        "strong_model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
    },
    "anthropic": {
        "weak_model": "claude-instant-1",
        "strong_model": "claude-2",
        "temperature": 0.7,
        "max_tokens": 1000,
    },
    "huggingface": {
        "weak_model": "phi-3-mini",
        "strong_model": "Llama3-70b",
        "temperature": 0.7,
        "max_length": 1000,
    },
}
