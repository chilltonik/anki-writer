from unittest.mock import MagicMock, patch

import pytest

from anki_writer.config import Settings
from anki_writer.translator import (
    DeepLTranslator,
    FakeTranslator,
    create_translator,
)


def test_deepl_translator_sends_expected_request_and_parses_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {"translations": [{"text": "He writes."}]}

    with patch("requests.post", return_value=mock_response) as mock_post:
        translator = DeepLTranslator(api_key="key123", host="https://api-free.deepl.com")
        result = translator.translate("Han skriver.", "norwegian", "English")

    assert result == "He writes."

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api-free.deepl.com/v2/translate"
    assert kwargs["headers"] == {"Authorization": "DeepL-Auth-Key key123"}
    assert kwargs["data"] == {
        "text": "Han skriver.",
        "source_lang": "NB",
        "target_lang": "EN-US",
    }
    mock_response.raise_for_status.assert_called_once()


def test_deepl_translator_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("boom")

    with patch("requests.post", return_value=mock_response):
        translator = DeepLTranslator(api_key="key123")
        with pytest.raises(Exception, match="boom"):
            translator.translate("Han skriver.", "norwegian", "English")


def test_deepl_translator_raises_on_malformed_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {}

    with patch("requests.post", return_value=mock_response):
        translator = DeepLTranslator(api_key="key123")
        with pytest.raises(RuntimeError, match="Unexpected DeepL response shape"):
            translator.translate("Han skriver.", "norwegian", "English")


def test_fake_translator_returns_canned_value():
    translator = FakeTranslator()
    assert translator.translate("any text", "norwegian", "English") == "Default translation."


def test_create_translator_returns_fake_translator_when_fake_true():
    settings = Settings(_env_file=None)
    translator = create_translator(settings, fake=True)
    assert isinstance(translator, FakeTranslator)


def test_create_translator_raises_without_api_key_when_not_fake():
    settings = Settings(_env_file=None, deepl_api_key=None)
    with pytest.raises(ValueError, match="DEEPL_API_KEY"):
        create_translator(settings, fake=False)


def test_create_translator_returns_deepl_translator_with_api_key():
    settings = Settings(_env_file=None, deepl_api_key="key123")
    translator = create_translator(settings, fake=False)
    assert isinstance(translator, DeepLTranslator)
