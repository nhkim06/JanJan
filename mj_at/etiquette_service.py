from __future__ import annotations

import json
import re
from typing import Any, Final

try:
    from .etiquette_prompts import (
        FOLLOWUP_INSTRUCTION,
        SYSTEM_INSTRUCTION,
        build_followup_prompt,
        build_report_prompt,
    )
    from .gemini_client import call_gemini
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
    from etiquette_prompts import (
        FOLLOWUP_INSTRUCTION,
        SYSTEM_INSTRUCTION,
        build_followup_prompt,
        build_report_prompt,
    )
    from gemini_client import call_gemini
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


def etiquette_villain_report(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
    category: str = "",
) -> AIResponse:
    """
    Main etiquette API function.

    First call:
        question = survey JSON string
        answer = JSON string with fullReport and summary

    Follow-up:
        question = plain text user message
        answer = plain English text
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
    if survey is not None:
        return _generate_report_response(lang, survey, histories, event_category)

    return _generate_followup_response(lang, histories, question, memory)


def parse_etiquette_answer(answer: str) -> dict[str, str]:
    data = json.loads(answer)
    if not isinstance(data, dict):
        raise ValueError("answer must be a JSON object.")
    return {
        "fullReport": str(data.get("fullReport", "")),
        "summary": str(data.get("summary", "")),
    }


def _generate_report_response(
    language: str,
    survey: list[dict[str, str]],
    histories: list[History],
    category: OccasionCategory,
) -> AIResponse:
    target_name = _target_name_from_histories(histories)
    prior_total, prior_rows = _prior_payments(histories, target_name)
    currency = _currency_from_histories(histories)

    prompt = build_report_prompt(
        language,
        survey,
        category,
        target_name,
        prior_total,
        prior_rows,
        currency,
    )
    gemini_response = call_gemini(
        prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.25,
        max_output_tokens=2500,
        json_mode=True,
    )
    if not gemini_response["success"]:
        return gemini_response

    try:
        # JSON 추출 시 마크다운 태그가 섞일 경우를 대비해 정규식 활용
        raw_answer = gemini_response["answer"]
        parsed = _extract_json_object(raw_answer)
        
        full_report = str(parsed.get("fullReport", "")).strip()
        summary = str(parsed.get("summary", "")).strip()
        
        # 프론트엔드에서 쉽게 쪼개 쓰도록 JSON 형태 그대로 반환 (추천)
        # 만약 하나의 문자열을 원한다면 아래와 같이 합칠 수 있습니다.
        combined_result = {
            "fullReport": full_report,
            "summary": summary
        }
        
        return {
            "success": True,
            "answer": json.dumps(combined_result, ensure_ascii=False)
        }
    except Exception as exc:
        return {"success": False, "answer": f"JSON Parsing Error: {str(exc)}"}


def _generate_followup_response(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
) -> AIResponse:
    target_name = _target_name_from_histories(histories)
    prior_total, _ = _prior_payments(histories, target_name)
    prompt = build_followup_prompt(question, memory, prior_total, target_name)
    return call_gemini(
        prompt,
        system_instruction=FOLLOWUP_INSTRUCTION,
        temperature=0.4,
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
