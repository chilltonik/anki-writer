import csv
import json

import pytest

from anki_writer.cli import _generate_validated, _resolve_concurrency, main, run
from anki_writer.config import Settings
from anki_writer.llm import ValidationOutput
from anki_writer.prompts import resolve_target_language


def test_cli_end_to_end_with_fake_generator(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    words_file = tmp_path / "words.json"
    words_file.write_text(json.dumps({"skriver": "пишет"}), encoding="utf-8")

    output_file = tmp_path / "output.txt"

    main([str(words_file), "norwegian", "--fake"])

    assert output_file.exists()

    lines = output_file.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[0] == "#separator:tab\n"
    assert lines[1] == "#html:true\n"

    reader = csv.reader(lines[2:], delimiter="\t", quotechar='"')
    rows = [row for row in reader if row and row != [""]]
    assert len(rows) == 1

    keyword, definition, example, translation = rows[0]
    assert keyword == "skriver"
    assert "skriver" in definition
    assert "пишет" in definition
    assert "Default sentence." in example
    assert translation == "Default translation."


def test_cli_concurrent_run_preserves_word_order(tmp_path):
    words = {"skriver": "пишет", "spiser": "ест", "leser": "читает", "sover": "спит"}
    words_file = tmp_path / "words.json"
    words_file.write_text(json.dumps(words), encoding="utf-8")

    output_file = tmp_path / "generated.txt"

    settings = Settings(_env_file=None, provider="ollama", concurrency=4, output=str(output_file))
    target_lang = resolve_target_language("norwegian")
    run(settings, str(words_file), "norwegian", target_lang, fake=True)

    lines = output_file.read_text(encoding="utf-8").splitlines(keepends=True)
    reader = csv.reader(lines[2:], delimiter="\t", quotechar='"')
    rows = [row for row in reader if row and row != [""]]

    assert [row[0] for row in rows] == list(words.keys())


@pytest.mark.parametrize(
    ("provider", "requested", "expected"),
    [
        ("hf", 4, 1),
        ("hf", 1, 1),
        ("ollama", 4, 4),
        ("fake", 4, 4),
        ("ollama", 0, 1),
    ],
)
def test_resolve_concurrency(provider, requested, expected):
    assert _resolve_concurrency(provider, requested) == expected


def test_generate_validated_passes_on_first_try():
    generate_calls = []
    validate_calls = []

    def generate():
        generate_calls.append(1)
        return "value"

    def validate(value):
        validate_calls.append(value)
        return ValidationOutput(is_valid=True)

    result = _generate_validated(generate, validate, max_attempts=2, label="thing", word="w")

    assert result == "value"
    assert len(generate_calls) == 1
    assert len(validate_calls) == 1


def test_generate_validated_regenerates_until_valid():
    attempts = iter(["bad1", "bad2", "good"])
    generate_calls = []

    def generate():
        value = next(attempts)
        generate_calls.append(value)
        return value

    def validate(value):
        return ValidationOutput(
            is_valid=(value == "good"), reason="" if value == "good" else "not good enough"
        )

    result = _generate_validated(generate, validate, max_attempts=2, label="thing", word="w")

    assert result == "good"
    assert generate_calls == ["bad1", "bad2", "good"]


def test_generate_validated_gives_up_after_max_attempts(caplog):
    generate_calls = []

    def generate():
        generate_calls.append(1)
        return "always bad"

    def validate(value):
        return ValidationOutput(is_valid=False, reason="never good enough")

    with caplog.at_level("WARNING"):
        result = _generate_validated(generate, validate, max_attempts=2, label="thing", word="w")

    assert result == "always bad"
    assert len(generate_calls) == 3
    assert "still failing validation" in caplog.text
