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


# DeepL uses "EN" for source but requires a region variant ("EN-US"/"EN-GB")
# for target; plain "EN" as a target code is deprecated by DeepL's API.
DEEPL_SOURCE_CODES = {
    "english": "EN",
    "norwegian": "NB",
    "polish": "PL",
    "russian": "RU",
}

DEEPL_TARGET_CODES = {
    "english": "EN-US",
    "norwegian": "NB",
    "polish": "PL",
    "russian": "RU",
}


def resolve_deepl_source_code(lang: str) -> str:
    normalized = lang.strip().lower()
    try:
        return DEEPL_SOURCE_CODES[normalized]
    except KeyError:
        supported = ", ".join(sorted(DEEPL_SOURCE_CODES))
        raise ValueError(
            f"No DeepL source language code for {lang!r}. Known: {supported}"
        ) from None


def resolve_deepl_target_code(lang: str) -> str:
    normalized = lang.strip().lower()
    try:
        return DEEPL_TARGET_CODES[normalized]
    except KeyError:
        supported = ", ".join(sorted(DEEPL_TARGET_CODES))
        raise ValueError(
            f"No DeepL target language code for {lang!r}. Known: {supported}"
        ) from None
