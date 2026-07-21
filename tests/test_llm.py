import json
from unittest.mock import MagicMock, patch

from anki_writer.llm import FakeSentenceGenerator, OllamaSentenceGenerator, SentenceOutput, TranslationOutput


def test_fake_sentence_generator_default_response():
    generator = FakeSentenceGenerator()
    sentence_result = generator.generate("any prompt", SentenceOutput)
    translation_result = generator.generate("any prompt", TranslationOutput)
    assert isinstance(sentence_result, SentenceOutput)
    assert sentence_result.sentence == "Default sentence."
    assert isinstance(translation_result, TranslationOutput)
    assert translation_result.translation == "Default translation."


def test_fake_sentence_generator_custom_response():
    generator = FakeSentenceGenerator(sentence="Han skriver.", translation="He writes.")
    assert generator.generate("prompt", SentenceOutput) == SentenceOutput(sentence="Han skriver.")
    assert generator.generate("prompt", TranslationOutput) == TranslationOutput(translation="He writes.")


def test_ollama_sentence_generator_sends_expected_request_and_parses_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": json.dumps({"translation": "He writes."})}
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        generator = OllamaSentenceGenerator(model="qwen2.5:1.5b", host="http://localhost:11434")
        result = generator.generate("some prompt", TranslationOutput)

    assert result == TranslationOutput(translation="He writes.")

    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["model"] == "qwen2.5:1.5b"
    assert kwargs["json"]["messages"] == [{"role": "user", "content": "some prompt"}]
    assert kwargs["json"]["format"] == TranslationOutput.model_json_schema()
    assert kwargs["json"]["stream"] is False
    mock_response.raise_for_status.assert_called_once()
