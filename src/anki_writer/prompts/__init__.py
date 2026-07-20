from importlib import resources

from anki_writer.languages import SUPPORTED_LANGUAGES, resolve_target_language

__all__ = ["SUPPORTED_LANGUAGES", "resolve_target_language", "build_prompt"]

_TEMPLATE = resources.files(__package__).joinpath("example_sentence.txt").read_text(encoding="utf-8")


def build_prompt(word: str, word_translation: str, source_lang: str, target_lang: str) -> str:
    return _TEMPLATE.format(
        word=word,
        word_translation=word_translation,
        source_lang=source_lang,
        target_lang=target_lang,
    )
