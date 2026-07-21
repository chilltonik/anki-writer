import html
import logging
import re

logger = logging.getLogger(__name__)


def mask_word_in_sentence(sentence: str, word: str, cloze_num: int = 1) -> str:
    """Wrap the first occurrence of `word` in `sentence` with Anki's native
    cloze syntax ({{cN::...}}). Falls back to the sentence unmasked (escaped,
    no cloze deletion) if `word` cannot be found in it."""
    match = re.search(rf"\b{re.escape(word)}\w*\b", sentence, re.IGNORECASE)
    if match is None:
        logger.warning("word %r not found in generated sentence, showing unmasked", word)
        return html.escape(sentence)

    matched_text = html.escape(match.group(0))
    before = html.escape(sentence[: match.start()])
    after = html.escape(sentence[match.end() :])
    return f"{before}{{{{c{cloze_num}::{matched_text}}}}}{after}"


def build_definition(word: str, word_translation: str, cloze_num: int = 1) -> str:
    return f"{{{{c{cloze_num}::{html.escape(word)}}}}} - {html.escape(word_translation)}"


def build_card(
    word: str, word_translation: str, example_sentence: str, example_translation: str
) -> tuple[str, str, str, str]:
    """Return (keyword, definition, example, translation) note field values,
    matching the real Anki note type's field order."""
    definition = build_definition(word, word_translation)
    example = mask_word_in_sentence(example_sentence, word)
    return word, definition, example, html.escape(example_translation)
