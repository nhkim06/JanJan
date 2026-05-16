from __future__ import annotations

from typing import Literal, TypedDict


LanguageCode = Literal["ko", "ja", "en"]
CultureBase = Literal["ko", "ja", "both", "unknown"]


class History(TypedDict):
    targetName: str
    received: bool
    value: int
    cultureBase: CultureBase
    category: str
    date: str


class AIResponse(TypedDict):
    success: bool
    answer: str
