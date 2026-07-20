from anki_writer.llm.base import ExampleOutput

DEFAULT_OLLAMA_MODEL = "qwen2.5:1.5b"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"


class OllamaSentenceGenerator:
    """Generates structured (sentence, translation) output from a model
    served by a local Ollama instance, using Ollama's structured-output
    support (JSON-schema passed via the `format` field) so the response is
    constrained to ExampleOutput's schema."""

    def __init__(self, model: str = DEFAULT_OLLAMA_MODEL, host: str = DEFAULT_OLLAMA_HOST):
        self._model = model
        self._host = host.rstrip("/")

    def generate(self, prompt: str) -> ExampleOutput:
        import requests

        response = requests.post(
            f"{self._host}/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "format": ExampleOutput.model_json_schema(),
                "stream": False,
            },
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return ExampleOutput.model_validate_json(content)
