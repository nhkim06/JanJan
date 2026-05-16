from __future__ import annotations

import json
import re
from typing import Any, Final

from google import genai
from google.genai.types import GenerateContentConfig

try:
    from ..ai_yk.type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from type_def import (
        AIResponse,
        CATEGORY_LABELS,
        OCCASION_CATEGORIES,
        CultureBase,
        History,
        OccasionCategory,
        is_occasion_category,
        validate_histories,
    )

MODEL = "gemini-2.5-flash"

ETIQUETTE_QUESTIONS: dict[OccasionCategory, list[str]] = {
    "birth": [
        "Is it acceptable to give a gift before the birth?",
        "May I visit the hospital or postpartum care center right after birth?",
        "What should I avoid saying to the new mother?",
        "May I take or post baby photos on social media?",
    ],
    "wedding": [
        "What is appropriate wedding attire?",
        "May I wear white or flashy clothing?",
        "May I bring an uninvited companion?",
    ],
    "employment": [
        "May I congratulate if the new job is not public yet?",
        "May I post congratulations on social media?",
        "May I congratulate a colleague's job change privately?",
    ],
    "school_admission": [
        "Should I acknowledge a friend's child's school enrollment?",
        "Is a message alone enough for a colleague's child's enrollment?",
    ],
    "business_opening": [
        "When and how should I visit to congratulate on a business opening?",
        "Is a personal gesture appropriate for this relationship?",
        "May I post promotional support on social media?",
    ],
    "first_birthday": [
        "May I take photos or post about the event on social media?",
    ],
    "funeral": [
        "Should I attend the funeral in person?",
        "What should I wear and how should I behave at the service?",
        "May I share obituary or funeral details with others?",
    ],
    "hospital_visit": [
        "Is an in-person hospital visit appropriate?",
        "If visiting, when and how should I go?",
        "Is a message alone acceptable without visiting?",
        "May I ask about the diagnosis or condition?",
        "May I share hospital room photos or admission details?",
    ],
}

ETIQUETTE_QUESTIONS_JA: dict[OccasionCategory, list[str]] = {
    "birth": [
        "When is the right time to give oshuku-zukai (birth celebration)?",
        "Should cash be avoided for birth gifts in Japan?",
        "Is giving a gift before birth acceptable in Japan?",
    ],
    "wedding": [
        "How to prepare and present goshugi (wedding gift envelope)?",
        "Taboo amounts or numbers for wedding gifts in Japan?",
        "How to reply to a wedding invitation?",
    ],
    "employment": ["Is cash natural for job-celebration gifts in Japan?"],
    "school_admission": [
        "Who should receive school-enrollment gifts in Japan?",
        "Is buying a randoseru as a gift appropriate?",
    ],
    "business_opening": [
        "Is public celebration of a business opening appropriate?",
        "Could a visit burden the other person?",
    ],
    "first_birthday": ["Rules for photos and SNS posts"],
    "funeral": [
        "Actions aligned with religion and funeral style",
        "Timeline for wake, funeral, and memorial services",
        "Whether to follow up through memorial rites for this relationship",
    ],
    "hospital_visit": [
        "Visiting hours, infection risk, and hospital rules",
        "Whether it is appropriate to ask about the illness in detail",
    ],
}

# Legacy Korean labels and English aliases from older clients
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

SYSTEM_INSTRUCTION = """You are an expert on Korean and Japanese ceremonial etiquette (weddings, funerals, births, openings, etc.).
Help the user avoid being an "etiquette villain" at life events.

Rules:
- Write ALL output in the target language specified in the user prompt.
- Do not calculate gift amounts; use the counterparty's past payments only for relationship depth and reciprocity.
- Mark uncertain points clearly in the target language.
- Be specific about visits, wording, dress code, SNS, timing, companions, and privacy.
- Apply norms for the given cultural base (Korea vs Japan)."""

FOLLOWUP_INSTRUCTION = """You are a ceremonial etiquette expert for Korea and Japan.
Answer the user's follow-up concisely in the target language specified in the user prompt, using the prior report and context."""


def _history_date(h: History) -> str:
    raw = h.get("date")
    if raw:
        return str(raw)
    legacy = h.get("date ")  # type: ignore[literal-required]
    return str(legacy or "")


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

    for h in reversed(histories):
        resolved = _normalize_category(h.get("category"))
        if resolved:
            return resolved

    return "wedding"


def _questions_for_category(
    category: OccasionCategory, currency: CultureBase | None
) -> list[str]:
    base = list(ETIQUETTE_QUESTIONS.get(category, []))
    if currency in ("ja", "both"):
        for q in ETIQUETTE_QUESTIONS_JA.get(category, []):
            if q not in base:
                base.append(q)
    return base


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
    for h in reversed(histories):
        currency = h.get("currency")
        if currency:
            return currency
    return None


def _prior_payments(
    histories: list[History], target_name: str | None
) -> tuple[int, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    total = 0
    for h in histories:
        if not h["received"]:
            continue
        if target_name and h["targetName"] != target_name:
            continue
        amount = int(h["value"])
        total += amount
        rows.append(
            {
                "targetName": h["targetName"],
                "value": amount,
                "currency": h["currency"],
                "category": h["category"],
                "date": _history_date(h),
            }
        )
    return total, rows


def _culture_label(currency: CultureBase | None, language: str) -> str:
    code = (currency or language or "ko").strip().lower()
    if code == "ja":
        return "Japan"
    if code == "ko":
        return "Korea"
    if code == "both":
        return "Korea and Japan"
    if code == "unknown":
        return "unspecified culture"
    return code


def _language_label(language: str) -> str:
    code = (language or "ko").strip().lower()
    if code == "ja":
        return "Japanese"
    if code == "en":
        return "English"
    return "Korean"


def _build_report_prompt(
    language: str,
    survey: list[dict[str, str]],
    category: OccasionCategory,
    target_name: str | None,
    prior_total: int,
    prior_rows: list[dict[str, Any]],
    currency: CultureBase | None,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    etiquette_checks = _questions_for_category(category, currency)
    checks_text = (
        "\n".join(f"- {q}" for q in etiquette_checks)
        if etiquette_checks
        else "- (general ceremonial etiquette)"
    )

    survey_text = "\n".join(
        f"Q: {item['question']}\nA: {item['answer']}" for item in survey
    )

    history_text = (
        json.dumps(prior_rows, ensure_ascii=False, indent=2)
        if prior_rows
        else "none"
    )

    culture_label = _culture_label(currency, language)
    output_language = _language_label(language)

    return f"""Using the pre-survey answers and ceremonial history below, write an **etiquette villain prevention analysis report**.

## Context
- Output language: {output_language} only (both fullReport and summary must be in {output_language})
- Cultural base for etiquette rules: {culture_label}
- Event category key: {category}
- Event category label: {category_label}
- Counterparty name: {target_name or "(not specified)"}
- Total amount the counterparty previously paid to the user (KRW): {prior_total:,}
- Payment history:
{history_text}

Payment history schema note:
- Each history item uses currency to mark the cash/culture context of that past amount.
- currency values are ko, ja, both, or unknown.

## Pre-survey (Q&A; questions/answers may be in Korean or Japanese—interpret them)
{survey_text}

## Etiquette checklist (address every item)
{checks_text}

## Output format (JSON only, no other text)
{{
  "fullReport": "Detailed markdown report written in {output_language}. Sections: Situation summary / What to do / What to avoid (villain points) / Visits, contact, SNS, wording / Culture-specific notes ({culture_label})",
  "summary": "3-5 sentences or 3-5 bullet points written in {output_language}"
}}
"""


def _build_followup_prompt(
    language: str,
    question: str,
    memory: str,
    prior_total: int,
    target_name: str | None,
) -> str:
    output_language = _language_label(language)

    return f"""## Target output language
{output_language} only

## Prior analysis report and context
{memory or "(none)"}

## Counterparty ceremonial payment summary
- Name: {target_name or "(not specified)"}
- Total paid to the user (KRW): {prior_total:,}

## User follow-up question
{question}
"""


def _call_gemini(
    user_prompt: str,
    *,
    followup: bool = False,
    json_mode: bool = False,
) -> str:
    client = genai.Client()
    system = FOLLOWUP_INSTRUCTION if followup else SYSTEM_INSTRUCTION
    config_kwargs: dict[str, Any] = {"system_instruction": system}
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"
    config = GenerateContentConfig(**config_kwargs)

    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=config,
    )
    return (response.text or "").strip()


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        data = json.loads(match.group())
        if isinstance(data, dict):
            return data

    raise ValueError("Could not parse JSON from Gemini response.")


def _generate_etiquette_report(
    language: str,
    survey: list[dict[str, str]],
    histories: list[History],
    category: OccasionCategory,
) -> dict[str, str]:
    target_name = _target_name_from_histories(histories)
    prior_total, prior_rows = _prior_payments(histories, target_name)
    currency = _currency_from_histories(histories)

    prompt = _build_report_prompt(
        language,
        survey,
        category,
        target_name,
        prior_total,
        prior_rows,
        currency,
    )
    raw = _call_gemini(prompt, json_mode=True)
    parsed = _extract_json_object(raw)

    full_report = str(parsed.get("fullReport", "")).strip()
    summary = str(parsed.get("summary", "")).strip()
    if not full_report or not summary:
        raise ValueError("fullReport or summary is empty.")

    return {"fullReport": full_report, "summary": summary}


def analyze_etiquette(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
    category: str = "",
) -> AIResponse:
    """
    Etiquette villain-prevention API entry point.

    First call: question is pre-survey JSON; answer is JSON with fullReport + summary.
    Follow-up: question is plain text; answer is plain text.
    """
    lang = (language or "ko").strip().lower()
    if lang not in ("ko", "ja", "en"):
        return {"success": False, "answer": f"Unsupported language: {language}"}

    if category.strip():
        normalized = _normalize_category(category)
        if normalized is None:
            allowed = ", ".join((*OCCASION_CATEGORIES, *CATEGORY_ALIASES))
            return {"success": False, "answer": f"category must be one of: {allowed}"}

    invalid_reason = validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    event_category = _resolve_category(histories, category or None)

    try:
        survey = _parse_survey(question)
        if survey is not None:
            report = _generate_etiquette_report(
                lang, survey, histories, event_category
            )
            return {
                "success": True,
                "answer": json.dumps(report, ensure_ascii=False),
            }

        target_name = _target_name_from_histories(histories)
        prior_total, _ = _prior_payments(histories, target_name)
        prompt = _build_followup_prompt(lang, question, memory, prior_total, target_name)
        reply = _call_gemini(prompt, followup=True)
        return {"success": True, "answer": reply}

    except Exception as exc:
        return {"success": False, "answer": str(exc)}


def parse_etiquette_answer(answer: str) -> dict[str, str]:
    data = json.loads(answer)
    if not isinstance(data, dict):
        raise ValueError("answer must be a JSON object.")
    return {
        "fullReport": str(data.get("fullReport", "")),
        "summary": str(data.get("summary", "")),
    }


if __name__ == "__main__":
    sample_histories: list[History] = [
        {
            "targetName": "홍길동",
            "received": True,
            "value": 50000,
            "currency": "ko",
            "category": "wedding",
            "date": "2026-05-16",
        }
    ]
    sample_survey = json.dumps(
        [
            {"question": "초대받은 상황인가요?", "answer": "정식으로 초대받음"},
            {"question": "결혼식에 참석하나요?", "answer": "참석하고 식사도 함"},
        ],
        ensure_ascii=False,
    )

    result = analyze_etiquette("en", sample_histories, sample_survey, "", "wedding")
    print(result)
