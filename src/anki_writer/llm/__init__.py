from typing import TYPE_CHECKING

from anki_writer.llm.base import ExampleOutput, FakeSentenceGenerator, SentenceGenerator
from anki_writer.llm.hf_provider import DEFAULT_HF_MODEL, HFSentenceGenerator
from anki_writer.llm.ollama_provider import DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL, OllamaSentenceGenerator

if TYPE_CHECKING:
    from anki_writer.config import Settings

__all__ = [
    "ExampleOutput",
    "SentenceGenerator",
    "FakeSentenceGenerator",
    "HFSentenceGenerator",
    "DEFAULT_HF_MODEL",
    "OllamaSentenceGenerator",
    "DEFAULT_OLLAMA_MODEL",
    "DEFAULT_OLLAMA_HOST",
    "create_generator",
]


def create_generator(
    settings: "Settings", *, fake: bool = False, model_override: str | None = None
) -> SentenceGenerator:
    if fake:
        return FakeSentenceGenerator()

    if settings.provider == "hf":
        return HFSentenceGenerator(
            model_name=model_override or settings.hf_model,
            device=settings.hf_device,
            max_new_tokens=settings.hf_max_new_tokens,
        )
    if settings.provider == "ollama":
        return OllamaSentenceGenerator(
            model=model_override or settings.ollama_model, host=settings.ollama_host
        )

    raise ValueError(f"Unsupported provider {settings.provider!r}. Supported: hf, ollama")
