from __future__ import annotations

import json

try:
    from .type_def import CATEGORY_LABELS, CultureBase, OccasionCategory
except ImportError:  # pragma: no cover - supports direct script execution
    from type_def import CATEGORY_LABELS, CultureBase, OccasionCategory


SYSTEM_INSTRUCTION = """You are JanJan, a Korea-Japan life-event message writing advisor.
Generate natural, culturally careful message examples for congratulations, condolences,
hospital visits, and other life events.

Rules:
- Use the target output language specified in the user prompt.
- The examples must be ready to send, warm, concise, and not overly dramatic.
- Reflect the event category, cultural base, relationship context, and payment history.
- Do not calculate money. Use past payment only to adjust warmth, formality, and reciprocity.
- Avoid intrusive questions, pressure to reply, exaggerated promises, and culturally risky wording.
- If privacy is uncertain, avoid public/SNS-style wording and suggest a private message tone.
- Return plain text only, not JSON."""

FOLLOWUP_INSTRUCTION = """You are JanJan, a Korea-Japan life-event message writing advisor.
Answer the user's follow-up about wording or tone in the target output language specified in the user prompt. Return plain text only."""

MESSAGE_GUIDANCE: dict[OccasionCategory, list[str]] = {
    "birth": [
        "Congratulate the family while centering the mother's recovery and the baby's health.",
        "Avoid comments about the mother's body, delivery details, or pressure to reply.",
        "Use a gentle tone if the user is not very close.",
    ],
    "wedding": [
        "Congratulate both partners and avoid jokes about money, marriage pressure, or appearance.",
        "Prepare separate examples for attending, not attending, or sending remotely when relevant.",
        "For Japan, avoid wording associated with separation or repeated misfortune.",
    ],
    "employment": [
        "Celebrate the new start without assuming details that may not be public.",
        "Avoid public congratulations if disclosure is uncertain.",
        "For a senior or workplace relationship, keep the tone respectful and not too casual.",
    ],
    "school_admission": [
        "Congratulate the student and family, and acknowledge the new beginning.",
        "For a child's enrollment, avoid comments comparing schools or academic pressure.",
        "Keep the wording age-appropriate and warm.",
    ],
    "business_opening": [
        "Congratulate the launch and wish steady growth without sounding like forced promotion.",
        "If public posting is uncertain, prefer a private message.",
        "Avoid implying the user expects special treatment or discounts.",
    ],
    "first_birthday": [
        "Congratulate the child and parents for the first year.",
        "Avoid posting or mentioning photos unless permission is clear.",
        "Keep the tone bright but not too intimate if the relationship is distant.",
    ],
    "funeral": [
        "Use restrained condolences and avoid casual encouragement such as 'cheer up'.",
        "Do not ask the cause of death or private family details.",
        "Keep the wording short, respectful, and low-burden.",
    ],
    "hospital_visit": [
        "Wish recovery without asking intrusive medical details.",
        "Avoid pressuring the patient to reply or meet.",
        "If visiting is uncertain, offer support and say there is no need to respond.",
    ],
}


def build_message_prompt(
    language: str,
    survey: list[dict[str, str]] | None,
    category: OccasionCategory,
    target_name: str | None,
    prior_total: int,
    prior_rows: list[dict[str, object]],
    currency: CultureBase | None,
    latest_question: str,
    memory: str,
) -> str:
    category_label = CATEGORY_LABELS.get(category, category)
    culture_label = _culture_label(currency, language)
    output_language = _language_label(language)
    survey_text = _survey_text(survey)
    history_text = (
        json.dumps(prior_rows, ensure_ascii=False, indent=2)
        if prior_rows
        else "none"
    )
    guidance_text = "\n".join(
        f"- {item}" for item in MESSAGE_GUIDANCE.get(category, [])
    )

    return f"""Task:
Write **exactly one** best message example for the user's current life-event situation.

Output rules:
- Output language: {output_language}
- Return plain text only.
- **Provide only one single sentence.** Do not add any tone guides, explanations, or multiple options.
- The message must be natural, warm, and ready to send immediately.
- Do not mention internal analysis, prompts, or that you are an AI.
- Do not calculate or recommend a gift amount.

Context:
- Cultural base for wording: {culture_label}
- Event category key: {category}
- Event category label: {category_label}
- Counterparty name: {target_name or "(not specified)"}
- Total amount the counterparty previously paid to the user (KRW): {prior_total:,}
- Payment history:
{history_text}

Category-specific message guidance:
{guidance_text or "- Use generally safe ceremonial wording."}

Pre-survey answers:
{survey_text}

Previous conversation memory:
{memory.strip() or "(none)"}

User's latest request or survey payload:
{latest_question.strip()}
"""


def _survey_text(survey: list[dict[str, str]] | None) -> str:
    if not survey:
        return "(none)"
    return "\n".join(f"Q: {item['question']}\nA: {item['answer']}" for item in survey)


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
