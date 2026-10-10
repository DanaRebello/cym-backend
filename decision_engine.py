"""
Decides what should happen next for a buyer.
Pure logic — no repo, no DB.

Actions (matching schema.sql CHECK constraint):
  CALL_UP    — escalate to broker for immediate contact
  NEGOTIATE  — recommend properties / work on price / keep engaging
"""


def decide_next_action(buyer: dict, matches, score: int, urgency: str,
                       breakdown: dict):
    """Return (action, reasoning)."""
    reasons = []

    # 1. Missing info → NEGOTIATE (agent keeps asking) — but we signal with CLARIFY intent
    missing = []
    if buyer.get("budget_max") is None:
        missing.append("budget")
    if not buyer.get("preferred_location"):
        missing.append("location")
    if not buyer.get("property_type"):
        missing.append("property type")
    if not buyer.get("purchase_timeline"):
        missing.append("timeline")

    if missing:
        reasons.append(f"Missing info: {', '.join(missing)}")
        return "NEGOTIATE", "; ".join(reasons)   # was CLARIFY

    # 2. High-budget, no timeline → suspect; keep negotiating
    budget = buyer.get("budget_max") or 0
    if budget > 10_00_00_000 and breakdown["urgency"] == 0:
        reasons.append("Large budget but no timeline — need intent first")
        return "NEGOTIATE", "; ".join(reasons)   # was CLARIFY

    # 3. No properties match → keep engaging
    if not matches:
        reasons.append("No matching properties in inventory")
        return "NEGOTIATE", "; ".join(reasons)   # was FOLLOW_UP

    # 4. High urgency + high score → escalate to broker
    if urgency == "HIGH" and score >= 60:
        reasons.append(f"High urgency; score={score}")
        reasons.append(f"Top match: {matches[0][0]['title']}")
        return "CALL_UP", "; ".join(reasons)     # was ESCALATE

    # 5. Decent score → recommend / negotiate
    if score >= 45:
        reasons.append(f"Score={score}; {len(matches)} match(es) found")
        return "NEGOTIATE", "; ".join(reasons)   # was RECOMMEND

    # 6. Low engagement → keep engaging
    reasons.append(f"Low score={score}; nurturing track")
    return "NEGOTIATE", "; ".join(reasons)       # was FOLLOW_UP