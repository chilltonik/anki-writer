from typing import Protocol

from pydantic import BaseModel


class ExampleOutput(BaseModel):
    sentence: str
    translation: str


class SentenceGenerator(Protocol):
    def generate(self, prompt: str) -> ExampleOutput: ...


class FakeSentenceGenerator:
    """Deterministic canned output for tests, no model download."""

    def __init__(self, response: ExampleOutput | None = None):
        self.response = response or ExampleOutput(
            sentence="Default sentence.", translation="Default translation."
        )

    def generate(self, prompt: str) -> ExampleOutput:
        return self.response
