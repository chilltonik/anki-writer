from typing import TYPE_CHECKING, Protocol

from anki_writer.languages import resolve_deepl_source_code, resolve_deepl_target_code

if TYPE_CHECKING:
    from anki_writer.config import Settings


class Translator(Protocol):
    def translate(self, text: str, source_lang: str, target_lang: str) -> str: ...


class DeepLTranslator:
    """Translates via the DeepL REST API. Raises on any failure (HTTP error,
    network error, or an unexpected response body) rather than silently
    falling back to anything else."""

    def __init__(self, api_key: str, host: str = "https://api-free.deepl.com"):
        self._api_key = api_key
        self._host = host.rstrip("/")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        import requests

        response = requests.post(
            f"{self._host}/v2/translate",
            headers={"Authorization": f"DeepL-Auth-Key {self._api_key}"},
            data={
                "text": text,
                "source_lang": resolve_deepl_source_code(source_lang),
                "target_lang": resolve_deepl_target_code(target_lang),
            },
        )
        response.raise_for_status()
        payload = response.json()
        try:
            return payload["translations"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError(f"Unexpected DeepL response shape: {payload!r}") from exc


class FakeTranslator:
    """Deterministic canned output for tests/`--fake` runs, no network call."""

    def __init__(self, translation: str = "Default translation."):
        self._translation = translation

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return self._translation


def create_translator(settings: "Settings", *, fake: bool = False) -> Translator:
    if fake:
        return FakeTranslator()

    if not settings.deepl_api_key:
        raise ValueError(
            "DEEPL_API_KEY is not set; a DeepL API key is required for translation "
            "(set it in .env or the environment, or pass --fake for a smoke test)"
        )
    return DeepLTranslator(api_key=settings.deepl_api_key, host=settings.deepl_api_host)
