import re
from typing import Optional, Dict, Any, List

# ─────────────────────────────────────────────
# INDUSTRY MAP (UNCHANGED BUT CLEANED)
# ─────────────────────────────────────────────
INDUSTRY_MAP = {
    "teollisuus": "Teollisuus",
    "industrial": "Teollisuus",
    "manufacturing": "Teollisuus",
    "factory": "Teollisuus",
    "production": "Teollisuus",
    "welding": "Teollisuus",
    "welder": "Teollisuus",
    "assembly": "Teollisuus",

    "logistics": "Logistiikka",
    "transport": "Logistiikka",
    "warehouse": "Logistiikka",
    "driver": "Logistiikka",

    "restaurant": "HoReCa",
    "hotel": "HoReCa",
    "chef": "HoReCa",
    "waiter": "HoReCa",

    "construction": "Rakennusala",
    "electrician": "Rakennusala",
    "plumber": "Rakennusala",
    "carpenter": "Rakennusala",

    "security": "Turvallisuusala",

    "healthcare": "Terveydenhuolto",
    "nurse": "Terveydenhuolto",
    "doctor": "Terveydenhuolto",
    "physician": "Terveydenhuolto",

    "it": "ICT / Teknologia",
    "software": "ICT / Teknologia",
    "developer": "ICT / Teknologia",
    "programmer": "ICT / Teknologia",
    "technology": "ICT / Teknologia",
    "tech": "ICT / Teknologia",

    "education": "Opetusala",
    "teacher": "Opetusala",
    "training": "Opetusala",
}

# ─────────────────────────────────────────────
# ROLE ONTOLOGY (🔥 MAIN FIX)
# ─────────────────────────────────────────────
INDUSTRY_ROLE_ONTOLOGY: Dict[str, List[str]] = {
    "Teollisuus": [
        "welder", "welding", "fabricator",
        "machinist", "cnc operator",
        "production worker", "factory worker",
        "assembly worker"
    ],

    "Logistiikka": [
        "driver", "truck driver", "courier",
        "warehouse worker", "forklift operator",
        "logistics coordinator"
    ],

    "HoReCa": [
        "chef", "cook", "waiter", "bartender",
        "kitchen assistant"
    ],

    "Rakennusala": [
        "carpenter", "electrician", "plumber",
        "construction worker", "builder"
    ],

    "ICT / Teknologia": [
        "software developer", "software engineer",
        "it developer", "it engineer",
        "backend developer", "frontend developer",
        "full stack developer", "web developer",
        "programmer", "devops engineer"
    ],

    "Terveydenhuolto": [
        "doctor", "physician", "nurse",
        "surgeon", "paramedic", "therapist"
    ]
}

# ─────────────────────────────────────────────
# CORRECTIONS (UNCHANGED)
# ─────────────────────────────────────────────
def correct_words(text: str) -> str:
    corrections = {
        "software devoloper": "software developer",
        "it developper": "it developer",
        "weldor": "welder",
        "weilder": "welder",
        "doctorr": "doctor",
        "nurs": "nurse",
    }

    for wrong, correct in corrections.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)

    return text


# ─────────────────────────────────────────────
# INDUSTRY PARSER (IMPROVED)
# ─────────────────────────────────────────────
def parse_industry(text: str) -> Optional[str]:
    text = text.lower()

    # 🔥 phrase-first matching (CRITICAL FIX)
    for industry, roles in INDUSTRY_ROLE_ONTOLOGY.items():
        if any(role in text for role in roles):
            return industry

    # fallback keyword map
    for keyword, industry in INDUSTRY_MAP.items():
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return industry

    return None


# ─────────────────────────────────────────────
# ROLE PARSER (FIXED + EXPANDED)
# ─────────────────────────────────────────────
def parse_role_keywords(text: str) -> List[str]:
    text_lower = text.lower()
    matched = []

    # 1. ontology match (PRIMARY FIX)
    for industry_roles in INDUSTRY_ROLE_ONTOLOGY.values():
        for role in industry_roles:
            if role in text_lower:
                matched.append(role)

    # 2. fallback keyword expansion
    ROLE_KEYWORD_MAP = {
        "developer": ["software developer", "developer", "engineer", "programmer"],
        "it developer": ["software developer", "engineer", "it specialist"],
        "welder": ["welder", "welding"],
        "driver": ["driver", "truck driver"],
        "nurse": ["nurse", "nursing"],
        "doctor": ["doctor", "physician"],
    }

    for key, roles in ROLE_KEYWORD_MAP.items():
        if key in text_lower:
            matched.extend(roles)

    return list(set(matched))


# ─────────────────────────────────────────────
# OTHER PARSERS (UNCHANGED)
# ─────────────────────────────────────────────
def parse_top_k(text: str) -> int:
    patterns = [r'top\s+(\d+)', r'show\s+(\d+)', r'find\s+(\d+)']
    text = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return 5


def parse_salary_range(text: str):
    match = re.search(r'(\d{3,5})\s+to\s+(\d{3,5})', text)
    if match:
        return {"min": int(match.group(1)), "max": int(match.group(2))}
    return None


def parse_location_filter(text: str):
    match = re.search(r'(\d+)\s*(km|kilometers?)', text.lower())
    return int(match.group(1)) if match else None


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def parse_voice_command(text: str, output_channel="slack", recipient_email=None):
    text = correct_words(text.lower())

    industry = parse_industry(text)
    role_keywords = parse_role_keywords(text)

    role_detected = bool(role_keywords)

    payload = {
        "query": text,
        "top_k": parse_top_k(text),
        "industry": industry,
        "role_keywords": role_keywords if role_keywords else None,
        "role_detected": role_detected,
        "salary_range": parse_salary_range(text),
        "location_filter": parse_location_filter(text),
        "output_channel": output_channel,
        "recipient_email": recipient_email,
    }

    return payload