import json
from unittest.mock import MagicMock, patch

from anki_writer.llm import ExampleOutput, FakeSentenceGenerator, OllamaSentenceGenerator


def test_fake_sentence_generator_default_response():
    generator = FakeSentenceGenerator()
    result = generator.generate("any prompt")
    assert isinstance(result, ExampleOutput)
    assert result.sentence == "Default sentence."
    assert result.translation == "Default translation."


def test_fake_sentence_generator_custom_response():
    custom = ExampleOutput(sentence="Han skriver.", translation="He writes.")
    generator = FakeSentenceGenerator(custom)
    assert generator.generate("prompt") is custom


def test_ollama_sentence_generator_sends_expected_request_and_parses_response():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {
            "content": json.dumps({"sentence": "Han skriver.", "translation": "He writes."})
        }
    }

    with patch("requests.post", return_value=mock_response) as mock_post:
        generator = OllamaSentenceGenerator(model="qwen2.5:1.5b", host="http://localhost:11434")
        result = generator.generate("some prompt")

    assert result == ExampleOutput(sentence="Han skriver.", translation="He writes.")

    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["model"] == "qwen2.5:1.5b"
    assert kwargs["json"]["messages"] == [{"role": "user", "content": "some prompt"}]
    assert kwargs["json"]["format"] == ExampleOutput.model_json_schema()
    assert kwargs["json"]["stream"] is False
    mock_response.raise_for_status.assert_called_once()
