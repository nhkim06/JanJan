from __future__ import annotations

from typing import Final


LANGUAGE_OUTPUT_NAMES: Final[dict[str, str]] = {
    "ko": "Korean (Hangul)",
    "kr": "Korean (Hangul)",
    "kor": "Korean (Hangul)",
    "korean": "Korean (Hangul)",
    "ja": "Japanese",
    "jp": "Japanese",
    "jpn": "Japanese",
    "japanese": "Japanese",
    "en": "English",
    "eng": "English",
    "english": "English",
}


def normalize_language_code(language: object) -> str:
    normalized = "".join(
        character
        for character in " ".join(str(language or "").strip().split())
        if character.isascii() and (character.isalnum() or character in {"-", "_"})
    )
    return normalized or "en"


def language_output_name(language: object) -> str:
    language_code = normalize_language_code(language)
    return LANGUAGE_OUTPUT_NAMES.get(
        language_code.casefold(),
        f"the language requested by code '{language_code}'",
    )


def language_output_rule(language: object) -> str:
    language_code = normalize_language_code(language)
    output_language = language_output_name(language_code)
    return (
        f"- requested_language_code: {language_code}\n"
        f"- target_output_language: {output_language}\n"
        "- Use only the target output language for all explanatory prose.\n"
        "- Keep exact provided proper names unchanged.\n"
        "- Do not choose or change the output language based on currency, country, "
        "culture_base, question text, survey text, or history."
    )
