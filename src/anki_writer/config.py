from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    log_level: Literal["INFO", "DEBUG"] = "INFO"
    provider: Literal["hf", "ollama"] = "hf"
    hf_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    hf_device: str | None = None
    hf_max_new_tokens: int = 300
    ollama_model: str = "qwen2.5:1.5b"
    ollama_host: str = "http://localhost:11434"
    output: str = "output.txt"
    concurrency: int = 1
    max_regenerate_attempts: int = 2
    deepl_api_key: str | None = None
    deepl_api_host: str = "https://api-free.deepl.com"
