from __future__ import annotations

import json
from typing import Final

try:
    from .gemini_client import call_gemini
    from .message_prompts import (
        FOLLOWUP_INSTRUCTION,
        SYSTEM_INSTRUCTION,
        build_message_prompt,
    )
    from .type_def import (
        AIResponse,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini
    from message_prompts import (
        FOLLOWUP_INSTRUCTION,
        SYSTEM_INSTRUCTION,
        build_message_prompt,
    )
    from type_def import (
        AIResponse,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )


CATEGORY_ALIASES: Final[dict[str, OccasionCategory]] = {
    "출산": "birth",
    "결혼": "wedding",
    "취업": "employment",
    "이직": "employment",
    "입학": "school_admission",
    "개업": "business_opening",
    "창업": "business_opening",
    "돌": "first_birthday",
    "돌잔치": "first_birthday",
    "첫돌": "first_birthday",
    "장례": "funeral",
    "부고": "funeral",
    "조문": "funeral",
    "병문안": "hospital_visit",
    "childbirth": "birth",
    "business": "business_opening",
}


def message_writing_guide(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
    category: str = "",
) -> AIResponse:
    """
    Message writing guide API.

    Input:
        pre-survey result in question + counterparty payment history in histories

    Output:
        plain text message examples
    """
    lang = (language or "ko").strip().lower()
    if lang not in ("ko", "ja", "en"):
        return {"success": False, "answer": f"Unsupported language: {language}"}

    if category.strip() and _normalize_category(category) is None:
        allowed = ", ".join((*OCCASION_CATEGORIES, *CATEGORY_ALIASES))
        return {"success": False, "answer": f"category must be one of: {allowed}"}

    invalid_reason = validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    event_category = _resolve_category(histories, category or None)
    survey = _parse_survey(question)
    target_name = _target_name_from_histories(histories)
    prior_total, prior_rows = _prior_payments(histories, target_name)
    currency = _currency_from_histories(histories)

    prompt = build_message_prompt(
        lang,
        survey,
        event_category,
        target_name,
        prior_total,
        prior_rows,
        currency,
        question,
        memory,
    )
    return call_gemini(
        prompt,
        system_instruction=FOLLOWUP_INSTRUCTION if survey is None else SYSTEM_INSTRUCTION,
        temperature=0.45,
        max_output_tokens=1800,
    )


def _normalize_category(raw: str | None) -> OccasionCategory | None:
    if not raw:
        return None
    normalized = raw.strip()
    normalized = CATEGORY_ALIASES.get(normalized, normalized)
    if is_occasion_category(normalized):
        return normalized
    return None


def _resolve_category(
    histories: list[History], explicit_category: str | None
) -> OccasionCategory:
    if explicit_category:
        resolved = _normalize_category(explicit_category)
        if resolved:
            return resolved

    for history in reversed(histories):
        resolved = _normalize_category(history.get("category"))
        if resolved:
            return resolved

    return "wedding"


def _parse_survey(question: str) -> list[dict[str, str]] | None:
    text = question.strip()
    if not text.startswith("["):
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, list):
        return None

    survey: list[dict[str, str]] = []
    for item in data:
        if isinstance(item, dict) and "question" in item and "answer" in item:
            survey.append(
                {"question": str(item["question"]), "answer": str(item["answer"])}
            )
    return survey if survey else None


def _target_name_from_histories(histories: list[History]) -> str | None:
    if not histories:
        return None
    return histories[-1]["targetName"]


def _currency_from_histories(histories: list[History]) -> CultureBase | None:
    for history in reversed(histories):
        currency = history.get("currency")
        if currency:
            return currency
    return None


def _prior_payments(
    histories: list[History], target_name: str | None
) -> tuple[int, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    total = 0
    for history in histories:
        if not history["received"]:
            continue
        if target_name and history["targetName"] != target_name:
            continue

        amount = int(history["value"])
        total += amount
        rows.append(
            {
                "targetName": history["targetName"],
                "value": amount,
                "currency": history["currency"],
                "category": history["category"],
                "date": _history_date(history),
            }
        )
    return total, rows


def _history_date(history: History) -> str:
    raw = history.get("date")
    if raw:
        return str(raw)
    legacy = history.get("date ")  # type: ignore[literal-required]
    return str(legacy or "")
