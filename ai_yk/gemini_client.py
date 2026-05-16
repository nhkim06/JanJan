from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

try:
    from .type_def import AIResponse
except ImportError:  # pragma: no cover - supports direct script execution
    from type_def import AIResponse


DEFAULT_MODEL = "gemini-2.5-flash"
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def call_gemini(
    prompt: str,
    *,
    system_instruction: str,
    temperature: float = 0.35,
    max_output_tokens: int = 2048,
) -> AIResponse:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "success": False,
            "answer": "Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY.",
        }

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    url = API_ENDPOINT.format(model=model)
    payload = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        },
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {"success": False, "answer": _format_error(exc.code, error_body)}
    except urllib.error.URLError as exc:
        return {"success": False, "answer": f"Gemini API connection failed: {exc.reason}"}
    except TimeoutError:
        return {"success": False, "answer": "Gemini API request timed out."}

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return {"success": False, "answer": "Gemini API returned invalid JSON."}

    answer = _extract_text(data)
    if not answer:
        return {"success": False, "answer": "Gemini API returned an empty response."}

    return {"success": True, "answer": answer}


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def pretty_question(raw_question: str) -> str:
    raw_question = raw_question.strip()
    if not raw_question:
        return ""

    try:
        parsed = json.loads(raw_question)
    except json.JSONDecodeError:
        return raw_question

    return pretty_json(parsed)


def _extract_text(data: dict[str, Any]) -> str:
    candidates = data.get("candidates") or []
    if not candidates:
        return ""

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "\n".join(part for part in text_parts if part).strip()


def _format_error(status_code: int, error_body: str) -> str:
    try:
        parsed = json.loads(error_body)
    except json.JSONDecodeError:
        return f"Gemini API request failed with HTTP {status_code}: {error_body}"

    message = parsed.get("error", {}).get("message") or error_body
    return f"Gemini API request failed with HTTP {status_code}: {message}"
