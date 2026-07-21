import csv
import json

import pytest

from anki_writer.cli import _resolve_concurrency, main, run
from anki_writer.config import Settings
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
