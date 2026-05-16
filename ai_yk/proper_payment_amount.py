from __future__ import annotations

from typing import Any, Final

try:
    from .gemini_client import call_gemini, pretty_json, pretty_question
    from .type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini, pretty_json, pretty_question
    from type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )


BASE_SYSTEM_INSTRUCTION = """
You are JanJan, an etiquette and cost advisor for Korean and Japanese life-event customs.
Give practical, culturally careful guidance for congratulations, condolences, visits, gifts,
cash gifts, and wording. Consider reciprocity from the payment history, but do not treat it
as a rigid debt. Avoid stereotypes, explain uncertainty, and prefer options that reduce
social burden. Answer only in the requested language.
""".strip()

BIRTH_SYSTEM_INSTRUCTION = """
""".strip()

WEDDING_SYSTEM_INSTRUCTION = """
""".strip()

EMPLOYMENT_SYSTEM_INSTRUCTION = """
""".strip()

SCHOOL_ADMISSION_SYSTEM_INSTRUCTION = """
""".strip()

BUSINESS_OPENING_SYSTEM_INSTRUCTION = """
""".strip()

FIRST_BIRTHDAY_SYSTEM_INSTRUCTION = """
""".strip()

FUNERAL_SYSTEM_INSTRUCTION = """
""".strip()

HOSPITAL_VISIT_SYSTEM_INSTRUCTION = """
""".strip()

CATEGORY_ALIASES: Final[dict[str, OccasionCategory]] = {
    "childbirth": "birth",
    "business": "business_opening",
}


def proper_payment_amount(
    language: str,
    histories: list[History],
    question: Any,
    category: str,
) -> AIResponse:
    normalized_category = _normalize_category(category)
    if normalized_category is None:
        allowed = ", ".join((*OCCASION_CATEGORIES, *CATEGORY_ALIASES))
        return {"success": False, "answer": f"category must be one of: {allowed}"}

    invalid_reason = validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    prompt = _build_prompt(language, histories, question, normalized_category)
    return call_gemini(
        prompt,
        system_instruction=_system_instruction_for_category(normalized_category),
        temperature=0.25,
        max_output_tokens=2500,
    )


def _build_prompt(
    language: str,
    histories: list[History],
    question: Any,
    category: OccasionCategory,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    return f"""
Task:
Create an analysis report about gifts and cash etiquette for the current event, then
recommend one proper congratulations/condolence payment amount.

Output rules:
- Answer in language code: {language}
- Return plain text only.
- Output exactly two top-level sections:
  1. report:
  2. recommended_amount:
- In report, explain the concrete social context inferred from the pre-survey answers,
  the gift/cash-gift reasoning, relevant reciprocity from payment history, etiquette risks,
  and any missing factors that make the recommendation uncertain.
- In recommended_amount, give one clear amount. Include the currency or culturally implied
  unit when it can be inferred from the question or histories.
- If there is not enough information, still give the safest conservative amount and briefly
  name the missing factors in the report.
- Use the payment history only when it is relevant to this person, relationship, category,
  timing, currency/culture marker, or reciprocity context.

Payment history schema note:
- Each history item uses currency to mark the cash/culture context of that past amount.
- currency values are ko, ja, both, or unknown.

Current event category:
- key: {category}
- label: {category_label}

Pre-survey answers:
{_format_question_data(question)}

Payment history:
{pretty_json(histories)}
""".strip()


def _normalize_category(category: str) -> OccasionCategory | None:
    normalized = category.strip()
    normalized = CATEGORY_ALIASES.get(normalized, normalized)
    if is_occasion_category(normalized):
        return normalized
    return None


def _system_instruction_for_category(category: OccasionCategory) -> str:
    if category == "birth":
        category_instruction = BIRTH_SYSTEM_INSTRUCTION
    elif category == "wedding":
        category_instruction = WEDDING_SYSTEM_INSTRUCTION
    elif category == "employment":
        category_instruction = EMPLOYMENT_SYSTEM_INSTRUCTION
    elif category == "school_admission":
        category_instruction = SCHOOL_ADMISSION_SYSTEM_INSTRUCTION
    elif category == "business_opening":
        category_instruction = BUSINESS_OPENING_SYSTEM_INSTRUCTION
    elif category == "first_birthday":
        category_instruction = FIRST_BIRTHDAY_SYSTEM_INSTRUCTION
    elif category == "funeral":
        category_instruction = FUNERAL_SYSTEM_INSTRUCTION
    elif category == "hospital_visit":
        category_instruction = HOSPITAL_VISIT_SYSTEM_INSTRUCTION
    else:
        category_instruction = ""

    if not category_instruction:
        return BASE_SYSTEM_INSTRUCTION
    return f"{BASE_SYSTEM_INSTRUCTION}\n\n{category_instruction}"


def _format_question_data(question: Any) -> str:
    if isinstance(question, str):
        return pretty_question(question)
    return pretty_json(question)
