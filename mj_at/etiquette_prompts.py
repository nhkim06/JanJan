from __future__ import annotations

import json

try:
    from .type_def import CATEGORY_LABELS, CultureBase, OccasionCategory
except ImportError:  # pragma: no cover - supports direct script execution
    from type_def import CATEGORY_LABELS, CultureBase, OccasionCategory


SYSTEM_INSTRUCTION = """You are an expert on Korean and Japanese ceremonial etiquette (weddings, funerals, births, openings, etc.).
Help the user avoid being an "etiquette villain" at life events.

Rules:
- Write ALL output in English only (fullReport, summary, and every follow-up reply).
- Do not calculate gift amounts.
- Mark uncertain points as "needs confirmation".
- Be specific about visits, wording, dress code, SNS, timing, companions, and privacy.

[Critical Etiquette Checkpoints]:
1. Birth: Check visit permission; avoid insensitive comments about weight/recovery; respect photo privacy (no SNS without consent)[cite: 50].
2. Wedding: No white/flashy outfits [cite: 55]; no uninvited guests[cite: 55]; Japan-specific: 'Goshugi' envelope etiquette and taboo numbers (4, 9)[cite: 53, 54].
3. Funeral: Dark formal attire[cite: 35]; do not ask about the cause of death; Japan-specific: check for 'Meibutsu' or religious styles[cite: 32, 34].
4. Hospital: Check visiting hours/infection risks [cite: 41, 42]; do not post room photos on SNS [cite: 46]; avoid asking sensitive illness details[cite: 45].
5. Business Opening: Check busy hours before visiting [cite: 66]; personal vs. public promotion preference[cite: 67].

[Output Format]:
You MUST respond in valid JSON format ONLY:
{
  "fullReport": "Detailed markdown analysis in English.",
  "summary": "3-5 bullet points of critical warnings in English."
}"""

FOLLOWUP_INSTRUCTION = """You are a ceremonial etiquette expert for Korea and Japan.
Answer the user's follow-up concisely in English only, using the prior report and context."""

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


def build_report_prompt(
    language: str,
    survey: list[dict[str, str]],
    category: OccasionCategory,
    target_name: str | None,
    prior_total: int,
    prior_rows: list[dict[str, object]],
    currency: CultureBase | None,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    checks_text = _checks_text(category, currency)
    survey_text = "\n".join(
        f"Q: {item['question']}\nA: {item['answer']}" for item in survey
    )
    history_text = (
        json.dumps(prior_rows, ensure_ascii=False, indent=2)
        if prior_rows
        else "none"
    )
    culture_label = _culture_label(currency, language)

    return f"""Using the pre-survey answers and ceremonial history below, write an **etiquette villain prevention analysis report**.

## Context
- Output language: English only (both fullReport and summary must be in English)
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
  "fullReport": "Detailed markdown report in English. Sections: Situation summary / What to do / What to avoid (villain points) / Visits, contact, SNS, wording / Culture-specific notes ({culture_label})",
  "summary": "English summary: 3-5 sentences or 3-5 bullet points"
}}
"""


def build_followup_prompt(
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


def _checks_text(category: OccasionCategory, currency: CultureBase | None) -> str:
    checks = list(ETIQUETTE_QUESTIONS.get(category, []))
    if currency in ("ja", "both"):
        for question in ETIQUETTE_QUESTIONS_JA.get(category, []):
            if question not in checks:
                checks.append(question)
    if not checks:
        return "- (general ceremonial etiquette)"
    return "\n".join(f"- {question}" for question in checks)


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
