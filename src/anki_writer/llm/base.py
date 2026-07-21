from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SentenceOutput(BaseModel):
    sentence: str


class TranslationOutput(BaseModel):
    translation: str


class SentenceGenerator(Protocol):
    def generate(self, prompt: str, output_type: type[T]) -> T: ...


class FakeSentenceGenerator:
    """Deterministic canned output for tests, no model download."""

    def __init__(self, sentence: str = "Default sentence.", translation: str = "Default translation."):
        self.sentence = sentence
        self.translation = translation

    def generate(self, prompt: str, output_type: type[T]) -> T:
        if output_type is SentenceOutput:
            return SentenceOutput(sentence=self.sentence)
        if output_type is TranslationOutput:
            return TranslationOutput(translation=self.translation)
        raise ValueError(f"Unsupported output_type {output_type!r}")
