SUPPORTED_LANGUAGES = {
    "english": "Russian",
    "norwegian": "English",
    "polish": "English",
}


def resolve_target_language(source_lang: str) -> str:
    normalized = source_lang.strip().lower()
    try:
        return SUPPORTED_LANGUAGES[normalized]
    except KeyError:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(f"Unsupported language {source_lang!r}. Supported: {supported}") from None
