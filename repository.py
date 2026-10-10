"""
DATA ACCESS CONTRACT
--------------------
Abstract interface that the database teammate must implement.

DO NOT put SQL here. This file is a pure interface.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class RealEstateRepository(ABC):
    """Abstract contract for all DB operations."""

    # ---------- BUYERS ----------
    @abstractmethod
    def create_buyer(self, name: str, phone: str = None, email: str = None) -> str:
        """Create a new buyer. Returns buyer_id."""
        ...

    @abstractmethod
    def get_buyer(self, buyer_id: str) -> Optional[Dict[str, Any]]:
        """Return buyer dict or None.
        Keys: buyer_id, name, phone, email, budget_min, budget_max,
              preferred_location, property_type, bedrooms,
              purchase_timeline, financing_ready, status
        """
        ...

    @abstractmethod
    def update_buyer_preferences(self, buyer_id: str, **fields) -> None:
        """Update only the supplied fields. Ignores None values."""
        ...

    # ---------- PROPERTIES ----------
    @abstractmethod
    def get_all_properties(self) -> List[Dict[str, Any]]:
        """Return list of available property dicts.
        Keys: property_id, title, price, location, property_type,
              bedrooms, available
        """
        ...

    @abstractmethod
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        ...

    # ---------- QUALIFICATIONS ----------
    @abstractmethod
    def save_qualification(
        self,
        buyer_id: str,
        budget_min: Optional[float],
        budget_max: Optional[float],
        location_prefs: Optional[str],
        timeline_months: Optional[int],
        score: float,
        urgency: str,
        action: str,
        reasoning: str,
        matched_property_id: Optional[str],
    ) -> int:
        """Persist a qualification. Returns qualification_id."""
        ...

    @abstractmethod
    def get_latest_qualification(self, buyer_id: str) -> Optional[Dict[str, Any]]:
        ...

    # ---------- CONVERSATION LOGS ----------
    @abstractmethod
    def log_message(
        self,
        buyer_id: str,
        sender: str,
        message_text: str,
        detected_intent: Optional[str] = None,
    ) -> None:
        ...

    @abstractmethod
    def get_conversation(self, buyer_id: str) -> List[Dict[str, Any]]:
        ...