from importlib import resources

from anki_writer.languages import SUPPORTED_LANGUAGES, resolve_target_language

__all__ = [
    "SUPPORTED_LANGUAGES",
    "resolve_target_language",
    "build_sentence_prompt",
    "build_translation_prompt",
]

_SENTENCE_TEMPLATE = resources.files(__package__).joinpath("example_sentence.txt").read_text(encoding="utf-8")
_TRANSLATE_TEMPLATE = resources.files(__package__).joinpath("translate_sentence.txt").read_text(encoding="utf-8")


def build_sentence_prompt(word: str, word_translation: str, source_lang: str) -> str:
    return _SENTENCE_TEMPLATE.format(
        word=word,
        word_translation=word_translation,
        source_lang=source_lang,
    )


def build_translation_prompt(
    sentence: str, word: str, word_translation: str, source_lang: str, target_lang: str
) -> str:
    return _TRANSLATE_TEMPLATE.format(
        sentence=sentence,
        word=word,
        word_translation=word_translation,
        source_lang=source_lang,
        target_lang=target_lang,
    )
