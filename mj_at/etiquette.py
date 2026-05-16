"""
Etiquette villain-prevention API — re-exports from ai_yk.etiquette_api.

Backend call:
    result = analyze_etiquette(language, histories, question, memory, category="wedding")
    # result["success"]: bool
    # result["answer"]: str
"""

from __future__ import annotations

try:
    from .etiquette_api import analyze_etiquette, parse_etiquette_answer
    from ..ai_yk.type_def import AIResponse, History
except ImportError:  # pragma: no cover - direct script execution
    import sys
    from pathlib import Path

    _AI_YK = Path(__file__).resolve().parents[1] / "ai_yk"
    if str(_AI_YK) not in sys.path:
        sys.path.insert(0, str(_AI_YK))
    from etiquette_api import analyze_etiquette, parse_etiquette_answer  # type: ignore[import-not-found]
    from type_def import AIResponse, History  # type: ignore[import-not-found]

__all__ = ["analyze_etiquette", "parse_etiquette_answer", "AIResponse", "History"]
