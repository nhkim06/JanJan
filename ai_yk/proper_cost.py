from __future__ import annotations

try:
    from .gemini_client import call_gemini, pretty_json, pretty_question
    from .type_def import AIResponse, History, validate_histories
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini, pretty_json, pretty_question
    from type_def import AIResponse, History, validate_histories


SYSTEM_INSTRUCTION = """
You are JanJan, an etiquette and cost advisor for Korean and Japanese life-event customs.
Give practical, culturally careful guidance for congratulations, condolences, visits, gifts,
cash gifts, and wording. Consider reciprocity from the payment history, but do not treat it
as a rigid debt. Avoid stereotypes, explain uncertainty, and prefer options that reduce
social burden. Answer only in the requested language.
""".strip()


def func(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
) -> AIResponse:
    invalid_reason = validate_histories(histories)
    if invalid_reason:
        return {"success": False, "answer": invalid_reason}

    prompt = _build_prompt(language, histories, question, memory)
    return call_gemini(
        prompt,
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.25,
        max_output_tokens=2500,
    )


def _build_prompt(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
) -> str:
    return f"""
Task:
Create an analysis report and recommend one proper payment amount for the current event.

Output rules:
- Answer in language code: {language}
- Return plain text only.
- Start with: recommended_amount: <integer>
- Then include a short report with these sections:
  1. why this amount fits
  2. cultural etiquette notes
  3. what to avoid
  4. optional alternatives if the user wants to give less or more
- If there is not enough information, still give a conservative range and name the missing factors.
- Use the payment history only when it is relevant to the same person, relationship, category, or culture.

Pre-survey answers:
{pretty_question(question)}

Payment history:
{pretty_json(histories)}

Conversation memory:
{memory.strip() or "(none)"}
""".strip()
