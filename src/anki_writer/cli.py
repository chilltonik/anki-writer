import argparse
import json
import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from anki_writer.cards import build_card
from anki_writer.config import Settings
from anki_writer.llm import SentenceGenerator, SentenceOutput, ValidationOutput, create_generator
from anki_writer.prompts import (
    build_sentence_prompt,
    build_sentence_validation_prompt,
    resolve_target_language,
)
from anki_writer.translator import Translator, create_translator
from anki_writer.writer import AnkiExportWriter

logger = logging.getLogger(__name__)


def configure_logging(log_level: str) -> None:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def load_words(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _generate_validated(
    generate: Callable[[], str],
    validate: Callable[[str], ValidationOutput],
    max_attempts: int,
    label: str,
    word: str,
) -> str:
    """Call `generate`, then `validate` its result; if invalid, call `generate`
    again and re-validate, up to `max_attempts` regenerations. Returns the last
    generated value regardless of whether it ultimately passed validation."""
    overall_start = time.perf_counter()
    attempt = 1
    gen_start = time.perf_counter()
    value = generate()
    logger.info(
        "%s for %r: generation attempt %d took %.2fs",
        label,
        word,
        attempt,
        time.perf_counter() - gen_start,
    )

    while True:
        val_start = time.perf_counter()
        result = validate(value)
        val_elapsed = time.perf_counter() - val_start
        logger.info(
            "%s for %r: validation of attempt %d took %.2fs -> %s%s",
            label,
            word,
            attempt,
            val_elapsed,
            "valid" if result.is_valid else "invalid",
            f" ({result.reason})" if not result.is_valid else "",
        )
        if result.is_valid:
            logger.info(
                "%s for %r validated successfully after %d attempt(s), total %.2fs",
                label,
                word,
                attempt,
                time.perf_counter() - overall_start,
            )
            return value
        if attempt > max_attempts:
            logger.warning(
                "%s for %r still failing validation after %d regeneration(s), using last attempt "
                "(total %.2fs): %s",
                label,
                word,
                max_attempts,
                time.perf_counter() - overall_start,
                result.reason,
            )
            return value
        logger.warning(
            "%s for %r failed validation (attempt %d/%d), regenerating: %s",
            label,
            word,
            attempt,
            max_attempts,
            result.reason,
        )
        attempt += 1
        gen_start = time.perf_counter()
        value = generate()
        logger.info(
            "%s for %r: generation attempt %d took %.2fs",
            label,
            word,
            attempt,
            time.perf_counter() - gen_start,
        )


def _generate_card(
    generator: SentenceGenerator,
    translator: Translator,
    word: str,
    word_translation: str,
    source_lang: str,
    target_lang: str,
    max_regenerate_attempts: int,
) -> tuple[str, str, str, str]:
    logger.info("generating card for word %r", word)
    card_start = time.perf_counter()

    def generate_sentence() -> str:
        sentence_prompt = build_sentence_prompt(word, word_translation, source_lang)
        logger.debug("sentence prompt for %r:\n%s", word, sentence_prompt)
        sentence = generator.generate(sentence_prompt, SentenceOutput).sentence
        logger.debug("sentence response for %r: %r", word, sentence)
        return sentence

    def validate_sentence(sentence: str) -> ValidationOutput:
        validation_prompt = build_sentence_validation_prompt(
            word, word_translation, source_lang, sentence
        )
        return generator.generate(validation_prompt, ValidationOutput)

    sentence = _generate_validated(
        generate_sentence, validate_sentence, max_regenerate_attempts, "sentence", word
    )

    translate_start = time.perf_counter()
    translation = translator.translate(sentence, source_lang, target_lang)
    logger.info("translation for %r took %.2fs", word, time.perf_counter() - translate_start)
    logger.debug("translation response for %r: %r", word, translation)

    logger.info("finished card for word %r in %.2fs", word, time.perf_counter() - card_start)
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
    parser.add_argument(
        "language", help="Language of the words, e.g. 'norwegian', 'english', 'polish'"
    )
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
    translator = create_translator(settings, fake=fake)
    concurrency = _resolve_concurrency(settings.provider, settings.concurrency)
    logger.info("provider=%s concurrency=%d", settings.provider, concurrency)

    written = 0
    with AnkiExportWriter(settings.output) as export_writer:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [
                executor.submit(
                    _generate_card,
                    generator,
                    translator,
                    word,
                    word_translation,
                    language,
                    target_lang,
                    settings.max_regenerate_attempts,
                )
                for word, word_translation in words.items()
            ]

            try:
                for future in futures:
                    card = future.result()
                    export_writer.write_card(card)
                    written += 1
            except Exception:
                logger.exception(
                    "card generation failed after %d card(s) written; partial export saved to %s",
                    written,
                    settings.output,
                )
                raise

    logger.info("wrote %d card(s) to %s", written, settings.output)


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
