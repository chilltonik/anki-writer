from typing import Protocol, TypeVar, cast

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SentenceOutput(BaseModel):
    sentence: str


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
        is_valid: bool = True,
    ):
        self.sentence = sentence
        self.is_valid = is_valid

    def generate(self, prompt: str, output_type: type[T]) -> T:
        if output_type is SentenceOutput:
            return cast(T, SentenceOutput(sentence=self.sentence))
        if output_type is ValidationOutput:
            return cast(
                T,
                ValidationOutput(
                    is_valid=self.is_valid, reason="" if self.is_valid else "fake invalid"
                ),
            )
        raise ValueError(f"Unsupported output_type {output_type!r}")
