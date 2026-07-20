import os
from dataclasses import dataclass

from dotenv import load_dotenv

from anki_writer.llm.hf_provider import DEFAULT_HF_MODEL, DEFAULT_MAX_NEW_TOKENS
from anki_writer.llm.ollama_provider import DEFAULT_OLLAMA_HOST, DEFAULT_OLLAMA_MODEL

DEFAULT_OUTPUT = "output.txt"
DEFAULT_PROVIDER = "hf"


@dataclass
class Settings:
    provider: str = DEFAULT_PROVIDER
    hf_model: str = DEFAULT_HF_MODEL
    hf_device: str | None = None
    hf_max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    ollama_host: str = DEFAULT_OLLAMA_HOST
    output: str = DEFAULT_OUTPUT


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        provider=os.getenv("ANKI_WRITER_PROVIDER", DEFAULT_PROVIDER),
        hf_model=os.getenv("ANKI_WRITER_HF_MODEL", DEFAULT_HF_MODEL),
        hf_device=os.getenv("ANKI_WRITER_HF_DEVICE") or None,
        hf_max_new_tokens=int(os.getenv("ANKI_WRITER_HF_MAX_NEW_TOKENS", DEFAULT_MAX_NEW_TOKENS)),
        ollama_model=os.getenv("ANKI_WRITER_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        ollama_host=os.getenv("ANKI_WRITER_OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
        output=os.getenv("ANKI_WRITER_OUTPUT", DEFAULT_OUTPUT),
    )
