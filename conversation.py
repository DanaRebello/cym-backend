"""
Ties everything together: one call = one chat turn.
"""

from repository import RealEstateRepository
from extractor import (
    extract_preferences, get_missing_fields,
    ask_followup_question, detect_intent,
)
from property_matcher import find_matching_properties
from lead_scorer import calculate_qualification
from decision_engine import decide_next_action


def _count_user_turns(repo: RealEstateRepository, buyer_id: str) -> int:
    return sum(1 for m in repo.get_conversation(buyer_id)
               if m["sender"] == "User")


def _safe_log(repo, buyer_id, sender, text, intent=None):
    """
    Log a message. Prefers the full signature; falls back to the
    minimal one if the repo (e.g., SQLite adapter) doesn't accept
    `detected_intent`.
    """
    try:
        repo.log_message(buyer_id, sender, text, detected_intent=intent)
    except TypeError:
        repo.log_message(buyer_id, sender, text)


def handle_message(repo: RealEstateRepository, buyer_id: str, user_text: str) -> str:
    """Process one user turn. Returns the AI's reply."""
    # 1. Log the user message
    _safe_log(repo, buyer_id, "User", user_text, intent=detect_intent(user_text))

    # 2. Extract + persist preferences
    prefs = extract_preferences(user_text)
    if prefs:
        repo.update_buyer_preferences(buyer_id, **prefs)

    # 3. Reload buyer + add turn count for intent scoring
    buyer = repo.get_buyer(buyer_id)
    if buyer is None:
        return "Sorry, I couldn't find your record."
    buyer["_turn_count"] = _count_user_turns(repo, buyer_id)

    # 4. If info incomplete → ask follow-up, stop here
    missing = get_missing_fields(buyer)
    if missing:
        reply = ask_followup_question(missing)
        _safe_log(repo, buyer_id, "AI Agent", reply, intent="NEGOTIATE")
        return reply

    # 5. Match properties
    matches = find_matching_properties(repo, buyer)

    # 6. Score the lead
    score, urgency, breakdown = calculate_qualification(buyer, matches)

    # 7. Decide next action
    action, reasoning = decide_next_action(buyer, matches, score, urgency, breakdown)

    # 8. Persist qualification
    matched_id = matches[0][0]["property_id"] if matches else None
    repo.save_qualification(
        buyer_id=buyer_id,
        budget_min=buyer.get("budget_min"),
        budget_max=buyer.get("budget_max"),
        location_prefs=buyer.get("preferred_location"),
        timeline_months=None,
        score=score,
        urgency=urgency,
        action=action,
        reasoning=reasoning,
        matched_property_id=matched_id,
    )

    # 9. Update buyer status if qualified
    if score >= 60:
        repo.update_buyer_preferences(buyer_id, status="QUALIFIED")

    # 10. Build reply and log it
    reply = build_reply(action, matches, score, urgency)
    _safe_log(repo, buyer_id, "AI Agent", reply, intent=action)
    return reply


def build_reply(action: str, matches, score: int, urgency: str) -> str:
    if action == "CALL_UP":
        top = matches[0][0]["title"] if matches else "a matching property"
        return (f"Great — you're a strong match! I've flagged your inquiry "
                f"as high priority and a broker will contact you shortly. "
                f"Top match: {top}.")
    if action == "NEGOTIATE":
        if not matches:
            return ("Thanks! I'll keep looking and follow up when we have "
                    "properties that match your criteria.")
        titles = ", ".join(m[0]["title"] for m in matches[:3])
        return f"I found some properties you may like: {titles}. Want details?"
    return "Thanks for your interest."