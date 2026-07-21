import pytest

from anki_writer.prompts import (
    build_sentence_prompt,
    build_sentence_validation_prompt,
    build_translation_prompt,
    build_translation_validation_prompt,
    resolve_target_language,
)


def test_resolve_target_language_supported_languages():
    assert resolve_target_language("english") == "Russian"
    assert resolve_target_language("English") == "Russian"
    assert resolve_target_language("norwegian") == "English"
    assert resolve_target_language("Norwegian") == "English"
    assert resolve_target_language("polish") == "English"
    assert resolve_target_language("Polish") == "English"


def test_resolve_target_language_rejects_unsupported():
    with pytest.raises(ValueError, match="Unsupported language"):
        resolve_target_language("german")


def test_build_sentence_prompt_includes_word_and_source_lang():
    prompt = build_sentence_prompt("skriver", "пишет", "Norwegian")
    assert "skriver" in prompt
    assert "пишет" in prompt
    assert "Norwegian" in prompt
    assert '"sentence"' in prompt
    assert '"translation"' not in prompt
    assert "English" not in prompt


def test_build_translation_prompt_includes_sentence_word_and_languages():
    prompt = build_translation_prompt("Han skriver.", "skriver", "пишет", "Norwegian", "English")
    assert "Han skriver." in prompt
    assert "skriver" in prompt
    assert "пишет" in prompt
    assert "Norwegian" in prompt
    assert "English" in prompt
    assert '"translation"' in prompt


def test_build_sentence_validation_prompt_includes_word_hint_and_sentence():
    prompt = build_sentence_validation_prompt("skriver", "пишет", "Norwegian", "Han skriver et brev.")
    assert "skriver" in prompt
    assert "пишет" in prompt
    assert "Norwegian" in prompt
    assert "Han skriver et brev." in prompt
    assert '"is_valid"' in prompt


def test_build_translation_validation_prompt_includes_all_inputs():
    prompt = build_translation_validation_prompt(
        "Han skriver et brev.", "He writes a letter.", "skriver", "пишет", "Norwegian", "English"
    )
    assert "Han skriver et brev." in prompt
    assert "He writes a letter." in prompt
    assert "skriver" in prompt
    assert "пишет" in prompt
    assert "Norwegian" in prompt
    assert "English" in prompt
    assert '"is_valid"' in prompt
