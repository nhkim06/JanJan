from __future__ import annotations

from typing import Final, Literal, TypedDict


LanguageCode = Literal["ko", "ja", "en"]
CultureBase = Literal["ko", "ja", "both", "unknown"]
OccasionGroup = Literal["celebration", "condolence"]
OccasionCategory = Literal[
    "birth",
    "wedding",
    "employment",
    "school_admission",
    "business_opening",
    "first_birthday",
    "funeral",
    "hospital_visit",
]

OCCASION_GROUPS: Final[tuple[OccasionGroup, ...]] = (
    "celebration",
    "condolence",
)

OCCASION_CATEGORIES: Final[tuple[OccasionCategory, ...]] = (
    "birth",
    "wedding",
    "employment",
    "school_admission",
    "business_opening",
    "first_birthday",
    "funeral",
    "hospital_visit",
)

CATEGORY_LABELS: Final[dict[OccasionGroup | OccasionCategory, str]] = {
    "celebration": "Celebratory Occasions",
    "condolence": "Sympathy Occasions",
    "birth": "Birth",
    "wedding": "Wedding",
    "employment": "New Job",
    "school_admission": "School Admission",
    "business_opening": "Business Opening",
    "first_birthday": "First Birthday",
    "funeral": "Funeral",
    "hospital_visit": "Hospital Visit",
}

CATEGORY_GROUPS: Final[dict[OccasionCategory, OccasionGroup]] = {
    "birth": "celebration",
    "wedding": "celebration",
    "employment": "celebration",
    "school_admission": "celebration",
    "business_opening": "celebration",
    "first_birthday": "celebration",
    "funeral": "condolence",
    "hospital_visit": "condolence",
}


class History(TypedDict):
    targetName: str
    received: bool
    value: int
    cultureBase: CultureBase
    category: OccasionCategory
    date: str


class AIResponse(TypedDict):
    success: bool
    answer: str


def is_occasion_category(value: str) -> bool:
    return value in OCCASION_CATEGORIES


def validate_histories(histories: list[History]) -> str | None:
    for index, history in enumerate(histories):
        category = history.get("category")
        if not isinstance(category, str) or not is_occasion_category(category):
            allowed = ", ".join(OCCASION_CATEGORIES)
            return f"histories[{index}].category must be one of: {allowed}"
    return None
