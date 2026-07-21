from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SentenceOutput(BaseModel):
    sentence: str


class TranslationOutput(BaseModel):
    translation: str


class ValidationOutput(BaseModel):
    is_valid: bool
    reason: str = ""


class SentenceGenerator(Protocol):
    def generate(self, prompt: str, output_type: type[T]) -> T: ...


class FakeSentenceGenerator:
    """Deterministic canned output for tests, no model download."""

    def __init__(
        self,
        sentence: str = "Default sentence.",
        translation: str = "Default translation.",
        is_valid: bool = True,
    ):
        self.sentence = sentence
        self.translation = translation
        self.is_valid = is_valid

    def generate(self, prompt: str, output_type: type[T]) -> T:
        if output_type is SentenceOutput:
            return SentenceOutput(sentence=self.sentence)
        if output_type is TranslationOutput:
            return TranslationOutput(translation=self.translation)
        if output_type is ValidationOutput:
            return ValidationOutput(is_valid=self.is_valid, reason="" if self.is_valid else "fake invalid")
        raise ValueError(f"Unsupported output_type {output_type!r}")
