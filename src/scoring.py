from __future__ import annotations

from typing import Mapping


SCORE_FIELDS = [
    "sweetness",
    "acidity",
    "aroma",
    "texture",
    "mango_intensity",
    "value_for_money",
]


FRESH_MANGO_WEIGHTS = {
    "sweetness": 0.20,
    "acidity_balance": 0.15,
    "aroma": 0.20,
    "texture": 0.20,
    "mango_intensity": 0.15,
    "value_for_money": 0.10,
}


PREPARED_MANGO_WEIGHTS = {
    "sweetness": 0.15,
    "acidity_balance": 0.10,
    "aroma": 0.15,
    "texture": 0.20,
    "mango_intensity": 0.30,
    "value_for_money": 0.10,
}


CATEGORY_ALIASES = {
    "fresh mango": "Fresh Mango",
    "fresh mangoes": "Fresh Mango",
    "mango": "Fresh Mango",
    "gelato": "Gelato",
    "mango gelato": "Gelato",
    "sorbet": "Sorbet",
    "mango sorbet": "Sorbet",
    "dessert": "Dessert",
    "drink": "Drink",
    "savory dish": "Savory Dish",
    "savoury dish": "Savory Dish",
    "other": "Other",
    "other mango magic": "Other",
}


def _as_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_score(value: float, minimum: float = 0.0, maximum: float = 10.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_category(category: object) -> str:
    if category in (None, ""):
        return "Other"

    normalized = str(category).strip().lower()
    return CATEGORY_ALIASES.get(normalized, "Other")


def calculate_acidity_balance(acidity: object) -> float | None:
    raw_acidity = _as_float(acidity)
    if raw_acidity is None:
        return None

    acidity_score = clamp_score(raw_acidity)
    acidity_balance = 10 - abs(acidity_score - 5) * 2
    return clamp_score(acidity_balance)


def category_weights(category: object) -> dict[str, float]:
    if normalize_category(category) == "Fresh Mango":
        return FRESH_MANGO_WEIGHTS
    return PREPARED_MANGO_WEIGHTS


def calculate_final_score(values: Mapping[str, object]) -> float | None:
    weights = category_weights(values.get("category"))
    weighted_total = 0.0
    weight_total = 0.0

    for field, weight in weights.items():
        if field == "acidity_balance":
            score = calculate_acidity_balance(values.get("acidity"))
        else:
            score = _as_float(values.get(field))

        if score is None:
            continue

        weighted_total += clamp_score(score) * weight
        weight_total += weight

    if weight_total == 0:
        return None

    return round(weighted_total / weight_total, 1)
