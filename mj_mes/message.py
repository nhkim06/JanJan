"""Public entry point for the mj_mes message writing API."""

from __future__ import annotations

try:
    from .message_api import message_guide
    from .message_service import message_writing_guide
    from .type_def import AIResponse, History
except ImportError:  # pragma: no cover - direct script execution
    from message_api import message_guide
    from message_service import message_writing_guide
    from type_def import AIResponse, History

__all__ = [
    "message_guide",
    "message_writing_guide",
    "AIResponse",
    "History",
]
