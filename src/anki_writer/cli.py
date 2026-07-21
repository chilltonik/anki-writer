import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from anki_writer.cards import build_card
from anki_writer.config import Settings
from anki_writer.llm import SentenceGenerator, SentenceOutput, TranslationOutput, create_generator
from anki_writer.prompts import build_sentence_prompt, build_translation_prompt, resolve_target_language
from anki_writer.writer import write_anki_export

logger = logging.getLogger(__name__)


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def load_words(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _generate_card(
    generator: SentenceGenerator,
    word: str,
    word_translation: str,
    source_lang: str,
    target_lang: str,
) -> tuple[str, str, str, str]:
    logger.info("generating card for word %r", word)

    sentence_prompt = build_sentence_prompt(word, word_translation, source_lang)
    logger.debug("sentence prompt for %r:\n%s", word, sentence_prompt)
    sentence = generator.generate(sentence_prompt, SentenceOutput).sentence
    logger.debug("sentence response for %r: %r", word, sentence)

    translation_prompt = build_translation_prompt(sentence, word, word_translation, source_lang, target_lang)
    logger.debug("translation prompt for %r:\n%s", word, translation_prompt)
    translation = generator.generate(translation_prompt, TranslationOutput).translation
    logger.debug("translation response for %r: %r", word, translation)

    return build_card(word, word_translation, sentence, translation)


def _resolve_concurrency(provider: str, requested: int) -> int:
    if provider == "hf" and requested > 1:
        logger.warning(
            "hf provider does not support concurrent generation "
            "(single local model instance); running with concurrency=1"
        )
        return 1
    return max(1, requested)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Anki cards from a word list using a local LLM."
    )
    parser.add_argument("words_file", help="Path to JSON file: {word: translation}")
    parser.add_argument("language", help="Language of the words, e.g. 'norwegian', 'english', 'polish'")
    parser.add_argument(
        "--fake",
        action="store_true",
        help="Use FakeSentenceGenerator (no model download); for smoke testing",
    )
    return parser


def run(settings: Settings, words_file: str, language: str, target_lang: str, fake: bool) -> None:
    words = load_words(words_file)
    logger.info("loaded %d word(s) from %s", len(words), words_file)
    generator = create_generator(settings, fake=fake)
    concurrency = _resolve_concurrency(settings.provider, settings.concurrency)
    logger.info("provider=%s concurrency=%d", settings.provider, concurrency)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        cards = list(
            executor.map(
                lambda item: _generate_card(generator, item[0], item[1], language, target_lang),
                words.items(),
            )
        )

    write_anki_export(settings.output, cards)
    logger.info("wrote %d card(s) to %s", len(cards), settings.output)


def main(argv: list[str] | None = None) -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        target_lang = resolve_target_language(args.language)
    except ValueError as exc:
        parser.error(str(exc))

    run(settings, args.words_file, args.language, target_lang, args.fake)


if __name__ == "__main__":
    main()
