from typing import TYPE_CHECKING

from anki_writer.llm.base import (
    FakeSentenceGenerator,
    SentenceGenerator,
    SentenceOutput,
    TranslationOutput,
    ValidationOutput,
)
from anki_writer.llm.hf_provider import HFSentenceGenerator
from anki_writer.llm.ollama_provider import OllamaSentenceGenerator

if TYPE_CHECKING:
    from anki_writer.config import Settings

__all__ = [
    "SentenceOutput",
    "TranslationOutput",
    "ValidationOutput",
    "SentenceGenerator",
    "FakeSentenceGenerator",
    "HFSentenceGenerator",
    "OllamaSentenceGenerator",
    "create_generator",
]


def create_generator(settings: "Settings", *, fake: bool = False) -> SentenceGenerator:
    if fake:
        return FakeSentenceGenerator()

    if settings.provider == "hf":
        return HFSentenceGenerator(
            model_name=settings.hf_model,
            device=settings.hf_device,
            max_new_tokens=settings.hf_max_new_tokens,
        )
    if settings.provider == "ollama":
        return OllamaSentenceGenerator(model=settings.ollama_model, host=settings.ollama_host)

    raise ValueError(f"Unsupported provider {settings.provider!r}. Supported: hf, ollama")
