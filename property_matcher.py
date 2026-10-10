"""
Matches buyers to available properties.
Pure logic + one repo call. No SQL.
"""

from repository import RealEstateRepository


def _location_match(prop_loc: str, pref_loc):
    if not pref_loc:
        return True
    return pref_loc.strip().lower() in prop_loc.strip().lower()


def _budget_match(price: float, budget_min, budget_max):
    if budget_max is None:
        return True
    lo = budget_min or 0
    return lo <= price <= budget_max * 1.05   # 5% flexibility


def _type_match(prop_type: str, pref_type):
    if not pref_type:
        return True
    return pref_type.strip().lower() == prop_type.strip().lower()


def _bedroom_match(prop_beds, pref_beds):
    if pref_beds is None:
        return True
    return prop_beds == pref_beds


def score_property(prop: dict, prefs: dict) -> int:
    """Score a single property (0-100) against buyer preferences."""
    score = 0
    if _location_match(prop["location"], prefs.get("preferred_location")):
        score += 40
    if _budget_match(prop["price"], prefs.get("budget_min"), prefs.get("budget_max")):
        score += 30
    if _type_match(prop["property_type"], prefs.get("property_type")):
        score += 15
    if _bedroom_match(prop["bedrooms"], prefs.get("bedrooms")):
        score += 15
    return score


def find_matching_properties(
    repo: RealEstateRepository,
    prefs: dict,
    min_score: int = 40,
    top_n: int = 5,
):
    """Return list of (property, score) sorted by score desc."""
    results = []
    for prop in repo.get_all_properties():
        s = score_property(prop, prefs)
        if s >= min_score:
            results.append((prop, s))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]