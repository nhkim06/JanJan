from __future__ import annotations

try:
    from .gemini_client import call_gemini, pretty_json
    from .type_def import AIResponse, History, validate_histories
except ImportError:  # pragma: no cover - supports direct script execution
    from gemini_client import call_gemini, pretty_json
    from type_def import AIResponse, History, validate_histories


SYSTEM_INSTRUCTION = """
You are JanJan, a concise AI chat advisor for Korean and Japanese life-event etiquette.
Use the survey result, payment history, and previous conversation memory to answer the
user's latest question. Be specific, warm, and practical. When money is involved, give a
clear amount or range and explain the social reasoning briefly. Answer only in the
requested language.
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
        temperature=0.4,
        max_output_tokens=1800,
    )


def _build_prompt(
    language: str,
    histories: list[History],
    question: str,
    memory: str,
) -> str:
    return f"""
Task:
Answer the user's latest etiquette question.

Output rules:
- Answer in language code: {language}
- Return plain text only.
- Keep the answer focused on the user's question.
- If the user asks for a payment amount, include a specific amount or a short range.
- If the user's plan may create burden or violate etiquette, say so gently and suggest a safer action.

User's latest question:
{question.strip()}

Payment history:
{pretty_json(histories)}

Payment history schema note:
- Each history item uses currency to mark the cash/culture context of that past amount.
- currency values are ko, ja, both, or unknown.

Conversation memory:
{memory.strip() or "(none)"}
""".strip()
