"""Static page content (lists and dictionaries used by templates)."""

features = [
    {"icon": "M", "title": "Moisture", "text": "Capacitive sensing detects hydration."},
    {"icon": "pH", "title": "pH Balance", "text": "Liquid pH probe reads acid-alkaline state."},
    {"icon": "O", "title": "Oiliness", "text": "Blotting paper and light sensor quantify sebum."},
    {"icon": "I", "title": "Ingredient Guidance", "text": "Decision-tree algorithm suggests ingredients."},
]

steps = [
    "Press the sensors against your skin",
    "Get instant readings on the LCD",
    "Receive ingredient suggestions",
]

specs = [
    ("Controller", "ESP32"),
    ("Moisture Sensor", "YL-69"),
    ("pH Sensor", "PH-4502C"),
    ("Light Sensor", "BH1750"),
    ("Display", "16x2 LCD"),
    ("Estimated Cost", "Rs. 2,500"),
]

comparison = [
    ("VISIA Complexion", "14+", "4.2L - 16.8L"),
    ("HiMirror", "3", "8.4K - 25K"),
    ("Neutrogena Skin360", "3", "Free"),
    ("DermaSense", "3", "~2.5K"),
]

skin_types = [
    {"type": "Oily", "condition": "Oiliness greater than 60%"},
    {"type": "Dry", "condition": "Oiliness less than 20% and Moisture less than 40%"},
    {"type": "Combination", "condition": "Oiliness 20-60% and Moisture less than 40%"},
    {"type": "Normal", "condition": "Everything else (hydrated, oiliness not above 60%)"},
]

ingredients = [
    {"type": "Dry", "list": "Hyaluronic Acid, Glycerin, Ceramides"},
    {"type": "Oily", "list": "Niacinamide, Salicylic Acid, Zinc PCA"},
    {"type": "Combination", "list": "Lactic Acid, Vitamin B5"},
    {"type": "Normal", "list": "Vitamin C, Peptides"},
]

readings = [
    {"name": "Moisture", "meaning": "Low <40%: Dry. Normal 40-70%: Balanced. High >70%: Well-hydrated."},
    {"name": "pH", "meaning": "Healthy 4.5-5.8: Barrier intact. Acidic <4.5: Irritation. Alkaline >5.8: Compromised."},
    {"name": "Oiliness", "meaning": "Low <20%: Dry. Medium 20-60%: Normal. High >60%: Oily."},
]

calibrations = [
    {"name": "Moisture", "detail": "Two-point calibration on dry and wet skin. Range: 236 ADC units."},
    {"name": "pH", "detail": "Calibrated with pH 4.0 and pH 9.0 buffers. R-squared = 0.999."},
    {"name": "Oiliness", "detail": "Calibrated with clean and oil-saturated blotting paper. Range: 600 lux."},
]