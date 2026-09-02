from anki_writer.llm.base import T


class OllamaSentenceGenerator:
    """Generates structured output from a model served by a local Ollama
    instance, using Ollama's structured-output support (JSON-schema passed
    via the `format` field) so the response is constrained to the requested
    pydantic output_type's schema."""

    def __init__(self, model: str, host: str):
        self._model = model
        self._host = host.rstrip("/")

    def generate(self, prompt: str, output_type: type[T]) -> T:
        import requests

        response = requests.post(
            f"{self._host}/api/chat",
            json={
                "model": self._model,
                "messages": [{"role": "user", "content": prompt}],
                "format": output_type.model_json_schema(),
                "think": False,
                "stream": False,
            },
        )
        response.raise_for_status()
        content = response.json()["message"]["content"]
        return output_type.model_validate_json(content)
