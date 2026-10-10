"""
In-memory fake repo for developing/testing without the real DB.
Implements the RealEstateRepository interface.
"""

import uuid
from typing import Dict, List
from repository import RealEstateRepository


class FakeRepository(RealEstateRepository):
    def __init__(self):
        self.buyers: Dict[str, dict] = {}
        self.properties: List[dict] = [
            {"property_id": "P001", "title": "3BHK Lakeview Apartment",
             "price": 7_800_000, "location": "Kakkanad",
             "property_type": "Apartment", "bedrooms": 3, "available": 1},
            {"property_id": "P002", "title": "2BHK Cosy Flat",
             "price": 5_500_000, "location": "Edappally",
             "property_type": "Apartment", "bedrooms": 2, "available": 1},
            {"property_id": "P003", "title": "4BHK Luxury Villa",
             "price": 22_000_000, "location": "Kakkanad",
             "property_type": "Villa", "bedrooms": 4, "available": 1},
            {"property_id": "P004", "title": "3BHK Smart Home",
             "price": 8_200_000, "location": "Kakkanad",
             "property_type": "Apartment", "bedrooms": 3, "available": 1},
            {"property_id": "P005", "title": "2BHK Budget Flat",
             "price": 4_200_000, "location": "Kochi",
             "property_type": "Apartment", "bedrooms": 2, "available": 1},
            {"property_id": "P006", "title": "5-cent Plot Kakkanad",
             "price": 3_000_000, "location": "Kakkanad",
             "property_type": "Plot", "bedrooms": None, "available": 1},
        ]
        self.logs: List[dict] = []
        self.qualifications: List[dict] = []

    # ---------- BUYERS ----------
    def create_buyer(self, name, phone=None, email=None):
        bid = "B" + uuid.uuid4().hex[:6].upper()
        self.buyers[bid] = {
            "buyer_id": bid, "name": name, "phone": phone, "email": email,
            "budget_min": None, "budget_max": None,
            "preferred_location": None, "property_type": None,
            "bedrooms": None, "purchase_timeline": None,
            "financing_ready": 0, "status": "AMBIGUOUS",
        }
        return bid

    def get_buyer(self, buyer_id):
        return self.buyers.get(buyer_id)

    def update_buyer_preferences(self, buyer_id, **fields):
        if buyer_id not in self.buyers:
            return
        allowed = {
            "budget_min", "budget_max", "preferred_location",
            "property_type", "bedrooms", "purchase_timeline",
            "financing_ready", "status",
        }
        for k, v in fields.items():
            if k in allowed and v is not None:
                self.buyers[buyer_id][k] = v

    # ---------- PROPERTIES ----------
    def get_all_properties(self):
        return [p for p in self.properties if p["available"]]

    def get_property(self, property_id):
        return next(
            (p for p in self.properties if p["property_id"] == property_id),
            None,
        )

    # ---------- QUALIFICATIONS ----------
    def save_qualification(self, buyer_id, budget_min, budget_max,
                           location_prefs, timeline_months, score, urgency,
                           action, reasoning, matched_property_id):
        qid = len(self.qualifications) + 1
        self.qualifications.append({
            "id": qid,
            "buyer_id": buyer_id,
            "budget_min": budget_min, "budget_max": budget_max,
            "location_preferences": location_prefs,
            "timeline_months": timeline_months,
            "qualification_score": score,
            "urgency_level": urgency,
            "next_action": action,
            "decision_reasoning": reasoning,
            "matched_property_id": matched_property_id,
        })
        return qid

    def get_latest_qualification(self, buyer_id):
        found = [q for q in self.qualifications if q["buyer_id"] == buyer_id]
        return found[-1] if found else None

    # ---------- CONVERSATION ----------
    def log_message(self, buyer_id, sender, message_text, detected_intent=None):
        self.logs.append({
            "buyer_id": buyer_id, "sender": sender,
            "message_text": message_text, "detected_intent": detected_intent,
        })

    def get_conversation(self, buyer_id):
        return [l for l in self.logs if l["buyer_id"] == buyer_id]