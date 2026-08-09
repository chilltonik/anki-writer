import pytest
from pydantic import ValidationError

from anki_writer.config import Settings


def test_defaults_apply_with_no_env(monkeypatch):
    monkeypatch.delenv("PROVIDER", raising=False)
    settings = Settings(_env_file=None)

    assert settings.log_level == "INFO"
    assert settings.provider == "hf"
    assert settings.hf_model == "Qwen/Qwen2.5-1.5B-Instruct"
    assert settings.hf_device is None
    assert settings.hf_max_new_tokens == 300
    assert settings.ollama_model == "qwen2.5:1.5b"
    assert settings.ollama_host == "http://localhost:11434"
    assert settings.output == "output.txt"
    assert settings.concurrency == 1
    assert settings.max_regenerate_attempts == 2
    assert settings.deepl_api_key is None
    assert settings.deepl_api_host == "https://api-free.deepl.com"


def test_invalid_provider_raises():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, provider="unsupported")


def test_invalid_hf_max_new_tokens_raises():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, hf_max_new_tokens="not-a-number")


def test_env_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("PROVIDER", "ollama")
    monkeypatch.setenv("CONCURRENCY", "4")
    monkeypatch.setenv("MAX_REGENERATE_ATTEMPTS", "5")
    monkeypatch.setenv("DEEPL_API_KEY", "abc123")
    monkeypatch.setenv("DEEPL_API_HOST", "https://api.deepl.com")

    settings = Settings(_env_file=None)

    assert settings.provider == "ollama"
    assert settings.concurrency == 4
    assert settings.max_regenerate_attempts == 5
    assert settings.deepl_api_key == "abc123"
    assert settings.deepl_api_host == "https://api.deepl.com"
