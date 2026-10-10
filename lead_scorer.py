"""
Computes a qualification score (0-100) and urgency level for a buyer.
Pure logic — no repo, no DB.
"""


def _timeline_urgency(timeline: str) -> int:
    """Map free-text timeline to an urgency score 0-25."""
    if not timeline:
        return 0
    t = timeline.lower()
    if "week" in t or "asap" in t or "immediate" in t:
        return 25
    if "month" in t:
        return 18
    if "year" in t:
        return 8
    return 0


def _clarity_score(buyer: dict) -> int:
    """0-25 based on how complete the requirement is."""
    s = 0
    if buyer.get("budget_max") is not None:
        s += 10
    if buyer.get("preferred_location"):
        s += 8
    if buyer.get("property_type") and buyer.get("bedrooms"):
        s += 7
    return s


def _fit_score(matches) -> int:
    """0-30 scaled from the best property match score."""
    if not matches:
        return 0
    best = matches[0][1]     # top property score (0-100)
    return int(best * 0.30)  # scale to 0-30


def _intent_score(buyer: dict) -> int:
    """0-20: financing + engagement."""
    s = 0
    if buyer.get("financing_ready"):
        s += 10
    turns = buyer.get("_turn_count", 0)
    s += min(turns * 2, 10)
    return s


def calculate_qualification(buyer: dict, matches):
    """
    Returns (total_score, urgency_level, breakdown dict).

    Score components:
      - clarity  : 0-25
      - fit      : 0-30
      - urgency  : 0-25
      - intent   : 0-20
    """
    breakdown = {
        "clarity": _clarity_score(buyer),
        "fit": _fit_score(matches),
        "urgency": _timeline_urgency(buyer.get("purchase_timeline")),
        "intent": _intent_score(buyer),
    }
    total = sum(breakdown.values())

    # Urgency label — driven by timeline AND overall score
    if breakdown["urgency"] >= 18 and total >= 60:
        level = "HIGH"
    elif total >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return total, level, breakdown