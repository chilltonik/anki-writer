import argparse
import json

from anki_writer.cards import build_card
from anki_writer.config import Settings, load_settings
from anki_writer.llm import create_generator
from anki_writer.prompts import build_prompt, resolve_target_language
from anki_writer.writer import write_anki_export


def load_words(path: str) -> dict[str, str]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_arg_parser(settings: Settings) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Anki cards from a word list using a local LLM."
    )
    parser.add_argument("words_file", help="Path to JSON file: {word: translation}")
    parser.add_argument("language", help="Language of the words, e.g. 'norwegian', 'english', 'polish'")
    parser.add_argument("-o", "--output", default=settings.output, help="Path to write Anki text export")
    parser.add_argument(
        "--provider",
        default=settings.provider,
        choices=["hf", "ollama"],
        help="Model provider: local Hugging Face model or Ollama",
    )
    parser.add_argument("--model", default=None, help="Model name override for the selected provider")
    parser.add_argument("--device", default=settings.hf_device, help="cpu/cuda/auto (hf provider only)")
    parser.add_argument("--ollama-host", default=settings.ollama_host, help="Ollama server URL")
    parser.add_argument(
        "--fake",
        action="store_true",
        help="Use FakeSentenceGenerator (no model download); for smoke testing",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    settings = load_settings()
    parser = build_arg_parser(settings)
    args = parser.parse_args(argv)

    try:
        target_lang = resolve_target_language(args.language)
    except ValueError as exc:
        parser.error(str(exc))

    settings.provider = args.provider
    settings.hf_device = args.device
    settings.ollama_host = args.ollama_host

    words = load_words(args.words_file)
    generator = create_generator(settings, fake=args.fake, model_override=args.model)

    cards = []
    for word, word_translation in words.items():
        prompt = build_prompt(word, word_translation, args.language, target_lang)
        result = generator.generate(prompt)
        cards.append(build_card(word, word_translation, result.sentence, result.translation))

    write_anki_export(args.output, cards)
    print(f"Wrote {len(cards)} card(s) to {args.output}")


if __name__ == "__main__":
    main()
