"""
경조사 에티켓 빌런 방지 API (Gemini)

백엔드 호출 형식:
    result = func(language, histories, question, memory)
    # result["success"]: bool
    # result["answer"]: str  (JSON 문자열 또는 챗봇 답변 텍스트)
"""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

from google import genai
from google.genai.types import GenerateContentConfig

MODEL = "gemini-3-flash-preview"

# ---------------------------------------------------------------------------
# Per-category etiquette checkpoints (English; sent to Gemini)
# ---------------------------------------------------------------------------
ETIQUETTE_QUESTIONS: dict[str, list[str]] = {
    "출산": [
        "Is it acceptable to give a gift before the birth?",
        "May I visit the hospital or postpartum care center right after birth?",
        "What should I avoid saying to the new mother?",
        "May I take or post baby photos on social media?",
    ],
    "결혼": [
        "What is appropriate wedding attire?",
        "May I wear white or flashy clothing?",
        "May I bring an uninvited companion?",
    ],
    "취업": [
        "May I congratulate if the new job is not public yet?",
        "May I post congratulations on social media?",
        "May I congratulate a colleague's job change privately?",
    ],
    "이직": [
        "May I congratulate if the new job is not public yet?",
        "May I post congratulations on social media?",
        "May I congratulate a colleague's job change privately?",
    ],
    "입학": [
        "Should I acknowledge a friend's child's school enrollment?",
        "Is a message alone enough for a colleague's child's enrollment?",
    ],
    "개업": [
        "When and how should I visit to congratulate on a business opening?",
        "Is a personal gesture appropriate for this relationship?",
        "May I post promotional support on social media?",
    ],
    "창업": [
        "When and how should I visit to congratulate on a business opening?",
        "Is a personal gesture appropriate for this relationship?",
        "May I post promotional support on social media?",
    ],
    "돌": [
        "May I take photos or post about the event on social media?",
    ],
    "돌잔치": [
        "May I take photos or post about the event on social media?",
    ],
    "첫돌": [
        "May I take photos or post about the event on social media?",
    ],
    "장례": [
        "Should I attend the funeral in person?",
        "What should I wear and how should I behave at the service?",
        "May I share obituary or funeral details with others?",
    ],
    "부고": [
        "Should I attend the funeral in person?",
        "What should I wear and how should I behave at the service?",
        "May I share obituary or funeral details with others?",
    ],
    "조문": [
        "Should I attend the funeral in person?",
        "What should I wear and how should I behave at the service?",
        "May I share obituary or funeral details with others?",
    ],
    "병문안": [
        "Is an in-person hospital visit appropriate?",
        "If visiting, when and how should I go?",
        "Is a message alone acceptable without visiting?",
        "May I ask about the diagnosis or condition?",
        "May I share hospital room photos or admission details?",
    ],
}

# Extra checkpoints when cultural base is Japan
ETIQUETTE_QUESTIONS_JA: dict[str, list[str]] = {
    "출산": [
        "When is the right time to give oshuku-zukai (birth celebration)?",
        "Should cash be avoided for birth gifts in Japan?",
        "Is giving a gift before birth acceptable in Japan?",
    ],
    "결혼": [
        "How to prepare and present goshugi (wedding gift envelope)?",
        "Taboo amounts or numbers for wedding gifts in Japan?",
        "How to reply to a wedding invitation?",
    ],
    "취업": ["Is cash natural for job-celebration gifts in Japan?"],
    "입학": [
        "Who should receive school-enrollment gifts in Japan?",
        "Is buying a randoseru as a gift appropriate?",
    ],
    "개업": [
        "Is public celebration of a business opening appropriate?",
        "Could a visit burden the other person?",
    ],
    "돌잔치": ["Rules for photos and SNS posts"],
    "장례": [
        "Actions aligned with religion and funeral style",
        "Timeline for wake, funeral, and memorial services",
        "Whether to follow up through memorial rites for this relationship",
    ],
    "병문안": [
        "Visiting hours, infection risk, and hospital rules",
        "Whether it is appropriate to ask about the illness in detail",
    ],
}

CATEGORY_ALIASES: dict[str, str] = {
    "출산": "출산",
    "결혼": "결혼",
    "취업": "취업",
    "이직": "취업",
    "입학": "입학",
    "개업": "개업",
    "창업": "개업",
    "돌": "돌잔치",
    "돌잔치": "돌잔치",
    "첫돌": "돌잔치",
    "장례": "장례",
    "부고": "장례",
    "조문": "장례",
    "병문안": "병문안",
}

SYSTEM_INSTRUCTION = """You are an expert on Korean and Japanese ceremonial etiquette (weddings, funerals, births, openings, etc.).
Help the user avoid being an "etiquette villain" at life events.

Rules:
- Write ALL output in English only (fullReport, summary, and every follow-up reply).
- Do not calculate gift amounts; use the counterparty's past payments only for relationship depth and reciprocity.
- Mark uncertain points as "needs confirmation".
- Be specific about visits, wording, dress code, SNS, timing, companions, and privacy.
- Apply norms for the given cultural base (Korea vs Japan) even though you write in English."""

FOLLOWUP_INSTRUCTION = """You are a ceremonial etiquette expert for Korea and Japan.
Answer the user's follow-up concisely in English only, using the prior report and context."""


class History(TypedDict, total=False):
    targetName: str
    received: bool  # True: 상대가 나에게 지불, False: 내가 상대에게 지불
    value: int
    cultureBase: str  # "ko" | "ja"
    category: str
    date: str


class FuncResult(TypedDict):
    success: bool
    answer: str


def _history_date(h: History) -> str:
    """백엔드 필드 오타('date ') 대응."""
    return str(h.get("date") or h.get("date ") or "")


def _normalize_category(raw: str | None) -> str:
    if not raw:
        return "결혼"
    key = raw.strip()
    for alias, canonical in CATEGORY_ALIASES.items():
        if alias in key or key in alias:
            return canonical
    return key


def _questions_for_category(category: str, culture_base: str | None) -> list[str]:
    canonical = CATEGORY_ALIASES.get(category, category)
    base = list(
        ETIQUETTE_QUESTIONS.get(canonical, ETIQUETTE_QUESTIONS.get(category, []))
    )
    if (culture_base or "").lower() == "ja":
        extra = ETIQUETTE_QUESTIONS_JA.get(
            canonical, ETIQUETTE_QUESTIONS_JA.get(category, [])
        )
        for q in extra:
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
    return histories[-1].get("targetName") or histories[0].get("targetName")


def _prior_payments(
    histories: list[History], target_name: str | None
) -> tuple[int, list[dict[str, Any]]]:
    """상대방이 나에게 지불한 경조사(received=True) 합계 및 내역."""
    rows: list[dict[str, Any]] = []
    total = 0
    for h in histories:
        if not h.get("received"):
            continue
        if target_name and h.get("targetName") != target_name:
            continue
        amount = int(h.get("value") or 0)
        total += amount
        rows.append(
            {
                "targetName": h.get("targetName"),
                "value": amount,
                "category": h.get("category"),
                "cultureBase": h.get("cultureBase"),
                "date": _history_date(h),
            }
        )
    return total, rows


def _culture_from_histories(histories: list[History]) -> str | None:
    for h in reversed(histories):
        base = h.get("cultureBase")
        if base:
            return base
    return None


def _culture_label(culture_base: str | None, language: str) -> str:
    code = (culture_base or language or "ko").strip().lower()
    if code == "ja":
        return "Japan"
    if code == "ko":
        return "Korea"
    return code


def _build_report_prompt(
    language: str,
    survey: list[dict[str, str]],
    category: str,
    target_name: str | None,
    prior_total: int,
    prior_rows: list[dict[str, Any]],
    culture_base: str | None,
) -> str:
    etiquette_checks = _questions_for_category(category, culture_base)
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

    culture_label = _culture_label(culture_base, language)

    return f"""Using the pre-survey answers and ceremonial history below, write an **etiquette villain prevention analysis report**.

## Context
- Output language: English only (both fullReport and summary must be in English)
- Cultural base for etiquette rules: {culture_label}
- Event category: {category}
- Counterparty name: {target_name or "(not specified)"}
- Total amount the counterparty previously paid to the user (KRW): {prior_total:,}
- Payment history:
{history_text}

## Pre-survey (Q&A; questions/answers may be in Korean or Japanese—interpret them)
{survey_text}

## Etiquette checklist (address every item)
{checks_text}

## Output format (JSON only, no other text)
{{
  "fullReport": "Detailed markdown report in English. Sections: Situation summary / What to do / What to avoid (villain points) / Visits, contact, SNS, wording / Culture-specific notes ({culture_label})",
  "summary": "English summary: 3–5 sentences or 3–5 bullet points"
}}
"""


def _build_followup_prompt(
    question: str,
    memory: str,
    prior_total: int,
    target_name: str | None,
) -> str:
    return f"""## Prior analysis report and context
{memory or "(none)"}

## Counterparty ceremonial payment summary
- Name: {target_name or "(not specified)"}
- Total paid to the user (KRW): {prior_total:,}

## User follow-up question (reply in English only)
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
) -> dict[str, str]:
    target_name = _target_name_from_histories(histories)
    prior_total, prior_rows = _prior_payments(histories, target_name)
    culture_base = _culture_from_histories(histories)

    category = "결혼"
    if histories:
        category = _normalize_category(histories[-1].get("category"))
    for h in reversed(histories):
        if h.get("category"):
            category = _normalize_category(h.get("category"))
            break

    prompt = _build_report_prompt(
        language,
        survey,
        category,
        target_name,
        prior_total,
        prior_rows,
        culture_base,
    )
    raw = _call_gemini(prompt, json_mode=True)
    parsed = _extract_json_object(raw)

    full_report = str(parsed.get("fullReport", "")).strip()
    summary = str(parsed.get("summary", "")).strip()
    if not full_report or not summary:
        raise ValueError("fullReport or summary is empty.")

    return {"fullReport": full_report, "summary": summary}


def func(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
) -> FuncResult:
    """
    에티켓 빌런 방지 API 진입점.

    Parameters
    ----------
    language : str
        "ko" | "ja" | "en"
    histories : list[History]
        경조사 주고받은 이력 (received=True → 상대가 나에게 지불)
    question : str
        첫 호출: 사전조사 JSON 문자열
        이후: 사용자 챗봇 질문
    memory : str
        이전 분석 보고서·대화 맥락 (후속 질문용)

    Returns
    -------
    dict
        {"success": bool, "answer": str}
        첫 호출 시 answer는 {"fullReport","summary"} JSON 문자열 (내용은 영어)
        모든 Gemini 프롬프트·응답은 영어로 생성됩니다.
    """
    lang = (language or "ko").strip().lower()
    if lang not in ("ko", "ja", "en"):
        return {
            "success": False,
            "answer": json.dumps(
                {"error": f"Unsupported language: {language}"},
                ensure_ascii=False,
            ),
        }

    try:
        survey = _parse_survey(question)
        if survey is not None:
            report = _generate_etiquette_report(lang, survey, histories)
            return {
                "success": True,
                "answer": json.dumps(report, ensure_ascii=False),
            }

        target_name = _target_name_from_histories(histories)
        prior_total, _ = _prior_payments(histories, target_name)
        prompt = _build_followup_prompt(question, memory, prior_total, target_name)
        reply = _call_gemini(prompt, followup=True)
        return {"success": True, "answer": reply}

    except Exception as exc:
        return {
            "success": False,
            "answer": json.dumps(
                {"error": str(exc)},
                ensure_ascii=False,
            ),
        }


def parse_etiquette_answer(answer: str) -> dict[str, str]:
    """첫 호출 성공 시 answer JSON → fullReport, summary."""
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
            "cultureBase": "ko",
            "category": "결혼",
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

    result = func("ko", sample_histories, sample_survey, "")
    print("success:", result["success"])
    print("answer:", result["answer"][:500], "..." if len(result["answer"]) > 500 else "")
