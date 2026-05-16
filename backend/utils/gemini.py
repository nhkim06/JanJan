from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Any, TypedDict, cast


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


if TYPE_CHECKING:
    from ai_yk.type_def import History as AiYkHistory
    from mj_at.type_def import History as MjHistory


class GeminiResult(TypedDict):
    success: bool
    answer: str


_DOTENV_LOADED = False


def _load_dotenv_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)
    
    # Ensure GOOGLE_API_KEY is set for google-genai package
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and not os.getenv("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = gemini_key


def _load_dotenv_files() -> None:
    global _DOTENV_LOADED
    if _DOTENV_LOADED:
        return

    _DOTENV_LOADED = True
    seen: set[Path] = set()
    search_roots = (Path.cwd(), Path(__file__).resolve().parent)

    for root in search_roots:
        for directory in (root, *root.parents):
            dotenv_path = directory / ".env"
            if dotenv_path in seen:
                continue

            seen.add(dotenv_path)
            if dotenv_path.is_file():
                _load_dotenv_file(dotenv_path)


_load_dotenv_files()


def __wrapper_ai_yk_payment(
    language: str,
    histories: list[dict[str, Any]],
    question: Any,
    memory: str = "",
    *,
    category: str = "",
    culture_base: str | None = None,
) -> "GeminiResult":
    try:
        from ai_yk.proper_payment_amount import proper_payment_amount
    except Exception as exc:
        return _wrap_result(False, f"ai_yk payment import failed: {exc}")

    try:
        # Use culture_base as currency indicator for proper_payment_amount
        return cast(
            GeminiResult,
            proper_payment_amount(
                language,
                cast("list[AiYkHistory]", histories),
                question,
                category,
                currency=culture_base,
            ),
        )
    except Exception as exc:
        return _wrap_result(False, f"ai_yk payment failed: {exc}")


def __wrapper_ai_yk_question(
    language: str,
    histories: list[dict[str, Any]],
    user_question: str,
    memory: str,
    *,
    current_context: dict[str, Any] | None = None,
    category: str | None = None,
    target_name: str = "",
    culture_base: str | None = None,
) -> "GeminiResult":
    try:
        from ai_yk.question_api import question as question_answer
    except Exception as exc:
        return _wrap_result(False, f"ai_yk question import failed: {exc}")

    context = current_context or {}
    try:
        return cast(
            GeminiResult,
            question_answer(
                language,
                histories,
                user_question,
                memory,
                category=category,
                target_name=target_name,
                culture_base=culture_base,
                presurvey=context,
            ),
        )
    except Exception as exc:
        return _wrap_result(False, f"ai_yk question failed: {exc}")


def __wrapper_mj_etiquette(
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    category: str = "",
) -> "GeminiResult":
    try:
        from mj_at.etiquette_api import analyze_etiquette
    except Exception as exc:
        return _wrap_result(False, f"mj_at etiquette import failed: {exc}")

    mj_histories = [_with_currency(history) for history in histories]
    return cast(
        GeminiResult,
        analyze_etiquette(
            language,
            cast("list[MjHistory]", mj_histories),
            question,
            memory,
            category,
        ),
    )


def __wrapper_mj_message(
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    category: str = "",
) -> "GeminiResult":
    try:
        from mj_mes.message_api import message_guide
    except Exception as exc:
        return _wrap_result(False, f"mj_mes message import failed: {exc}")

    mj_histories = [_with_currency(history) for history in histories]
    return cast(
        GeminiResult,
        message_guide(
            language,
            cast("list[MjHistory]", mj_histories),
            question,
            memory,
            category,
        ),
    )


def get_ai_yk_payment_report(
    language: str,
    histories: list[dict[str, Any]],
    question: Any,
    category: str,
    culture_base: str | None = None,
) -> "GeminiResult":
    return __wrapper_ai_yk_payment(
        language, histories, question, category=category, culture_base=culture_base
    )


def get_ai_yk_question_answer(
    language: str,
    histories: list[dict[str, Any]],
    user_question: str,
    memory: str,
    *,
    current_context: dict[str, Any] | None = None,
    category: str | None = None,
    target_name: str = "",
    culture_base: str | None = None,
) -> "GeminiResult":
    return __wrapper_ai_yk_question(
        language,
        histories,
        user_question,
        memory,
        current_context=current_context,
        category=category,
        target_name=target_name,
        culture_base=culture_base,
    )


def get_mj_etiquette_answer(
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    category: str = "",
) -> "GeminiResult":
    return __wrapper_mj_etiquette(language, histories, question, memory, category=category)


def get_mj_message_answer(
    language: str,
    histories: list[dict[str, Any]],
    question: str,
    memory: str,
    category: str = "",
) -> "GeminiResult":
    return __wrapper_mj_message(language, histories, question, memory, category=category)


def _with_currency(history: dict[str, Any]) -> dict[str, Any]:
    if "currency" in history:
        return history

    normalized = dict(history)
    if "cultureBase" in normalized:
        normalized["currency"] = normalized["cultureBase"]
    return normalized


def _wrap_result(success: bool, answer: str) -> GeminiResult:
    return {
        "success": success,
        "answer": answer,
    }


def _pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


DEFAULT_MODEL = "gemini-2.0-flash"
