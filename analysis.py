"""Skin analysis engine.

Turns a Reading (moisture %, pH, oiliness %) into a SkinProfile using the
thresholds published on the site (see content.readings and content.skin_types).

Decision tree for skin type:
    oiliness > 60                      -> Oily
    oiliness < 20 and moisture < 40    -> Dry
    oiliness 20-60 and moisture < 40   -> Combination (oily but dehydrated)
    otherwise                          -> Normal

The old site text listed Combination and Normal with overlapping conditions.
The moisture split above is the rule used to separate them.
"""

from models import Reading, SkinProfile

# ---- Thresholds (single source of truth) ----
OIL_LOW = 20
OIL_HIGH = 60
MOISTURE_LOW = 40
MOISTURE_HIGH = 70
PH_ACIDIC = 4.5
PH_ALKALINE = 5.8

BASE_INGREDIENTS = {
    "Dry": ["Hyaluronic Acid", "Glycerin", "Ceramides"],
    "Oily": ["Niacinamide", "Salicylic Acid", "Zinc PCA"],
    "Combination": ["Lactic Acid", "Vitamin B5"],
    "Normal": ["Vitamin C", "Peptides"],
}

# Extra suggestions when pH is outside the healthy range
PH_ADJUSTMENTS = {
    "Acidic": ["Panthenol", "Centella Asiatica"],
    "Alkaline": ["Lactic Acid (low strength)", "Ceramides"],
}


def moisture_level(moisture):
    if moisture < MOISTURE_LOW:
        return "Low"
    if moisture <= MOISTURE_HIGH:
        return "Normal"
    return "High"


def oil_level(oiliness):
    if oiliness < OIL_LOW:
        return "Low"
    if oiliness <= OIL_HIGH:
        return "Medium"
    return "High"


def ph_status(ph):
    if ph < PH_ACIDIC:
        return "Acidic"
    if ph <= PH_ALKALINE:
        return "Healthy"
    return "Alkaline"


def classify_skin_type(reading):
    if reading.oiliness > OIL_HIGH:
        return "Oily"
    if reading.moisture < MOISTURE_LOW:
        return "Dry" if reading.oiliness < OIL_LOW else "Combination"
    return "Normal"


def suggest_ingredients(skin_type, status):
    suggestions = list(BASE_INGREDIENTS[skin_type])
    for item in PH_ADJUSTMENTS.get(status, []):
        if item not in suggestions:
            suggestions.append(item)
    return suggestions


def build_notes(reading, status, skin_type):
    notes = []
    if status == "Acidic":
        notes.append("Your skin is more acidic than the healthy range, which can go with irritation. Keep routines gentle.")
    elif status == "Alkaline":
        notes.append("Your skin is more alkaline than the healthy range, which can mean a weakened barrier. Avoid harsh cleansers.")
    if reading.moisture > MOISTURE_HIGH:
        notes.append("Moisture is high, so extra heavy moisturisers may not be needed.")
    if skin_type == "Combination":
        notes.append("Oil is in the normal range but hydration is low, so treat dehydration first.")
    notes.append("These are educational prototype readings, not a medical diagnosis.")
    return notes


def analyse(reading):
    """Return a SkinProfile for a Reading."""
    if not isinstance(reading, Reading):
        raise TypeError("analyse() expects a Reading")
    skin_type = classify_skin_type(reading)
    status = ph_status(reading.ph)
    return SkinProfile(
        skin_type=skin_type,
        moisture_level=moisture_level(reading.moisture),
        ph_status=status,
        oil_level=oil_level(reading.oiliness),
        ingredients=suggest_ingredients(skin_type, status),
        notes=build_notes(reading, status, skin_type),
    )