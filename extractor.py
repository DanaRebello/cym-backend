"""
Extracts structured preferences from free-form buyer text.
Rule-based here; swap extract_preferences() with an LLM call in production.
"""

import re

REQUIRED_FIELDS = [
    "budget_max", "preferred_location", "property_type", "purchase_timeline",
]

KNOWN_LOCATIONS = [
    "kakkanad", "edappally", "kochi", "ernakulam",
    "thrissur", "kozhikode", "trivandrum",
]

PROPERTY_TYPE_ALIASES = {
    "flat": "Apartment", "apartment": "Apartment",
    "villa": "Villa", "house": "Villa",
    "plot": "Plot", "land": "Plot",
}


def extract_preferences(text: str) -> dict:
    """Parse buyer message → partial preference dict."""
    prefs = {}
    low = text.lower()

    # --- Budget ---
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lac|crore|cr|k)\b", low)
    if m:
        amt = float(m.group(1))
        unit = m.group(2)
        if unit in ("crore", "cr"):
            amt *= 10_000_000
        elif unit in ("lakh", "lac"):
            amt *= 100_000
        elif unit == "k":
            amt *= 1_000
        prefs["budget_max"] = int(amt)

    # --- Bedrooms ---
    m = re.search(r"(\d+)\s*(?:bhk|bedroom|bed|br)", low)
    if m:
        prefs["bedrooms"] = int(m.group(1))

    # --- Location ---
    for loc in KNOWN_LOCATIONS:
        if loc in low:
            prefs["preferred_location"] = loc.title()
            break

    # --- Property type ---
    for alias, canonical in PROPERTY_TYPE_ALIASES.items():
        if re.search(rf"\b{alias}\b", low):
            prefs["property_type"] = canonical
            break

    # --- Timeline ---
    if any(k in low for k in ["within a week", "asap", "immediate", "this week"]):
        prefs["purchase_timeline"] = "Within 1 week"
    elif "week" in low:
        prefs["purchase_timeline"] = "Within 2 weeks"
    elif "month" in low:
        prefs["purchase_timeline"] = "Within 3 months"
    elif "year" in low:
        prefs["purchase_timeline"] = "Within a year"

    # --- Financing ---
    if any(k in low for k in ["pre-approved", "preapproved", "loan approved", "sanctioned"]):
        prefs["financing_ready"] = 1
    elif "loan" in low or "financing" in low:
        prefs["financing_ready"] = 1

    return prefs


def get_missing_fields(buyer: dict) -> list:
    """Return list of REQUIRED_FIELDS not yet filled."""
    return [f for f in REQUIRED_FIELDS if not buyer.get(f)]


QUESTION_MAP = {
    "budget_max": "What is your approximate budget?",
    "preferred_location": "Which area or locality are you interested in?",
    "property_type": "Are you looking for an apartment, villa, or plot?",
    "purchase_timeline": "What is your expected purchase timeline?",
}


def ask_followup_question(missing_fields: list) -> str:
    """Compose a polite question covering missing fields."""
    parts = [QUESTION_MAP[f] for f in missing_fields if f in QUESTION_MAP]
    if not parts:
        return "Could you tell me a bit more about what you're looking for?"
    return " ".join(parts)


def detect_intent(text: str) -> str:
    """Rough intent classifier for logging."""
    low = text.lower()
    if any(k in low for k in ["buy", "purchase", "looking for", "interested"]):
        return "INQUIRY"
    if any(k in low for k in ["visit", "see", "schedule", "viewing"]):
        return "SCHEDULE"
    if any(k in low for k in ["price", "cost", "budget"]):
        return "PRICING"
    if any(k in low for k in ["no", "not interested", "cancel"]):
        return "WITHDRAW"
    return "OTHER"