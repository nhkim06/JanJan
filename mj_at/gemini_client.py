from __future__ import annotations

import os
from typing import Any

from google import genai
from google.genai.types import GenerateContentConfig

try:
    from .type_def import AIResponse
except ImportError:  # pragma: no cover - supports direct script execution
    from type_def import AIResponse


DEFAULT_MODEL = "gemini-3-flash-preview"


def call_gemini(
    prompt: str,
    *,
    system_instruction: str,
    temperature: float = 0.35,
    max_output_tokens: int = 2048,
    json_mode: bool = False,
) -> AIResponse:
    if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return {
            "success": False,
            "answer": "Gemini API key is missing. Set GEMINI_API_KEY or GOOGLE_API_KEY.",
        }

    model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    config_kwargs: dict[str, Any] = {
        "system_instruction": system_instruction,
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=GenerateContentConfig(**config_kwargs),
        )
    except Exception as exc:
        return {"success": False, "answer": f"Gemini API request failed: {exc}"}

    answer = (response.text or "").strip()
    if not answer:
        return {"success": False, "answer": "Gemini API returned an empty response."}
    return {"success": True, "answer": answer}
