import re
from typing import Optional, Dict, Any

INDUSTRY_MAP = {
    # Teollisuus (Industrial/Manufacturing)
    "teollisuus": "Teollisuus",
    "industrial": "Teollisuus",
    "manufacturing": "Teollisuus",
    "factory": "Teollisuus",
    "production": "Teollisuus",
    "welding": "Teollisuus",
    "welder": "Teollisuus",
    "assembly": "Teollisuus",
    
    # Logistiikka (Logistics)
    "logistiikka": "Logistiikka",
    "logistics": "Logistiikka",
    "transport": "Logistiikka",
    "shipping": "Logistiikka",
    "warehouse": "Logistiikka",
    "driver": "Logistiikka",
    "delivery": "Logistiikka",
    "courier": "Logistiikka",
    
    # HoReCa (Hotel/Restaurant/Catering)
    "horeca": "HoReCa",
    "hospitality": "HoReCa",
    "restaurant": "HoReCa",
    "hotel": "HoReCa",
    "catering": "HoReCa",
    "kitchen": "HoReCa",
    "chef": "HoReCa",
    "waiter": "HoReCa",
    "bartender": "HoReCa",
    "cook": "HoReCa",
    
    # Rakennusala (Construction)
    "rakennusala": "Rakennusala",
    "construction": "Rakennusala",
    "building": "Rakennusala",
    "contractor": "Rakennusala",
    "carpenter": "Rakennusala",
    "electrician": "Rakennusala",
    "plumber": "Rakennusala",
    
    # Turvallisuusala (Security)
    "turvallisuusala": "Turvallisuusala",
    "security": "Turvallisuusala",
    "guard": "Turvallisuusala",
    "safety": "Turvallisuusala",
    
    # Terveydenhuolto (Healthcare)
    "terveydenhuolto": "Terveydenhuolto",
    "healthcare": "Terveydenhuolto",
    "medical": "Terveydenhuolto",
    "hospital": "Terveydenhuolto",
    "nursing": "Terveydenhuolto",
    "nurse": "Terveydenhuolto",
    "doctor": "Terveydenhuolto",
    "care": "Terveydenhuolto",
    
    # Satama-ala (Port/Harbor)
    "satama-ala": "Satama-ala",
    "satama": "Satama-ala",
    "port": "Satama-ala",
    "harbor": "Satama-ala",
    "dock": "Satama-ala",
    "maritime": "Satama-ala",
    
    # ICT / Teknologia (IT/Technology)
    "ict": "ICT / Teknologia",
    "teknologia": "ICT / Teknologia",
    "it": "ICT / Teknologia",
    "technology": "ICT / Teknologia",
    "tech": "ICT / Teknologia",
    "software": "ICT / Teknologia",
    "developer": "ICT / Teknologia",
    "programming": "ICT / Teknologia",
    "programmer": "ICT / Teknologia",
    "coding": "ICT / Teknologia",
    
    # Kemia / Labra (Chemistry/Laboratory)
    "kemia": "Kemia / Labra",
    "labra": "Kemia / Labra",
    "chemistry": "Kemia / Labra",
    "laboratory": "Kemia / Labra",
    "lab": "Kemia / Labra",
    "chemist": "Kemia / Labra",
    
    # Ilmailu (Aviation)
    "ilmailu": "Ilmailu",
    "aviation": "Ilmailu",
    "aircraft": "Ilmailu",
    "flight": "Ilmailu",
    "airline": "Ilmailu",
    "pilot": "Ilmailu",
    
    # Opetusala (Education/Teaching)
    "opetusala": "Opetusala",
    "education": "Opetusala",
    "teaching": "Opetusala",
    "teacher": "Opetusala",
    "school": "Opetusala",
    "training": "Opetusala",
    
    # Puhtausala (Cleaning)
    "puhtausala": "Puhtausala",
    "cleaning": "Puhtausala",
    "cleaner": "Puhtausala",
    "janitor": "Puhtausala",
    "housekeeping": "Puhtausala",
}

def correct_words(text: str) -> str:
    corrections = {
        # Lahti
        "lottie": "lahti",
        "lotti": "lahti",
        "lottery": "lahti",
        "laahti": "lahti",
        "lahtti": "lahti",
        "lachti": "lahti",
        "lahty": "lahti",
        "loathe": "lahti",
        "latte": "lahti",
        
        # Helsinki
        "helsingki": "helsinki",
        "helsinky": "helsinki",
        "helsinski": "helsinki",
        "hellsinki": "helsinki",
        "helskinki": "helsinki",
        "helsingi": "helsinki",
        "helsenki": "helsinki",
        
        # Tampere
        "tamper": "tampere",
        "tampera": "tampere",
        "tamperre": "tampere",
        "tampare": "tampere",
        "tompere": "tampere",
        "tamperay": "tampere",
        
        # Turku
        "turkey": "turku",
        "turko": "turku",
        "turkoo": "turku",
        "turkku": "turku",
        
        # Oulu
        "olu": "oulu",
        "olou": "oulu",
        "oulo": "oulu",
        "owlu": "oulu",
        
        # Espoo
        "espo": "espoo",
        "espou": "espoo",
        "esspoo": "espoo",
        
        # Vantaa
        "vanta": "vantaa",
        "vantah": "vantaa",
        "wantaa": "vantaa",
        
        # Jyväskylä
        "jyvaskyla": "jyväskylä",
        "jyvaskila": "jyväskylä",
        "yuvaskyla": "jyväskylä",
        "jyvaskylla": "jyväskylä",
        "juvenskyla": "jyväskylä",
        
        # Kuopio
        "copio": "kuopio",
        "kwoopio": "kuopio",
        "kuopeo": "kuopio",
        
        # Kouvola
        "couvola": "kouvola",
        "kouwola": "kouvola",
        "kouvala": "kouvola",
        
        # Pori
        "pory": "pori",
        "poor": "pori",
        
        # Lappeenranta
        "lappenranta": "lappeenranta",
        "lapeenranta": "lappeenranta",
        "lapenranta": "lappeenranta",
        
        # Vaasa
        "vasa": "vaasa",
        "wasa": "vaasa",
        "vassa": "vaasa",
        
        # Rovaniemi
        "rovaniemy": "rovaniemi",
        "rovanemi": "rovaniemi",
        
        # Joensuu
        "joensoo": "joensuu",
        "yoensuu": "joensuu",
        "joensu": "joensuu",
        
        # Hämeenlinna
        "hameenlinna": "hämeenlinna",
        "hameen linna": "hämeenlinna",
        "hammelinna": "hämeenlinna",
        
        # Industry
        "logistic": "logistics",
        "logistick": "logistics",
        "logistiks": "logistics",
        "konstruktion": "construction",
        "health care": "healthcare",
        "healthkare": "healthcare",
        "resturant": "restaurant",
        "restarant": "restaurant",
        "sekurity": "security",
        "cleanning": "cleaning",
        "teknology": "technology",
        "techology": "technology",
        
        # Units
        "kilometer": "kilometers",
        "kilometre": "kilometers",
        "kilometres": "kilometers",
        "kilameter": "kilometers",
        
        # Salary
        "salery": "salary",
        "sallary": "salary",
    }
    text_corrected = text

    for wrong, correct in corrections.items():
        text_corrected  = re.sub(r'\b' + re.escape(wrong) + r'\b', correct,text_corrected, flags=re.IGNORECASE)
            
    return text_corrected

def parse_top_k(text: str) -> int:
    patterns = [
        r'top\s+(\d+)',
        r'show\s+(\d+)',
        r'find\s+(\d+)'
    ]
    text = text.lower()
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return 5

def parse_salary_range(text: str) -> Optional[Dict[str, int]]:
    text = text.lower()
    # Pattern 1: "xxxx to xxxx"
    match = re.search(r'(\d{3,5})\s+to\s+(\d{3,5})', text)
    if match:
        return {
            "min": int(match.group(1)),
            "max": int(match.group(2))
        }
    # Pattern 2: "between 3000 and 5000"
    match = re.search(r'between\s+(\d{3,5})\s+and\s+(\d{3,5})', text)
    if match:
        return {
            "min": int(match.group(1)),
            "max": int(match.group(2))
        }
    return None

def parse_industry(text: str) -> Optional[str]:
    text = text.lower()
    for keyword, industry in INDUSTRY_MAP.items():
        if keyword in text:
            return industry
    return None

def parse_location_filter(text: str) -> Optional[int]:
    text = text.lower()
    
    # Pattern 1: "within X km/kilometers"
    match = re.search(r'within\s+(\d+)\s*(?:kilometers?|km)', text)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "X km/kilometers"
    match = re.search(r'(\d+)\s*(?:kilometers?|km)', text)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "radius X"
    if 'radius' in text:
        match = re.search(r'(?:radius\s+)?(\d+)(?:\s+radius)?', text)
        if match:
            return int(match.group(1))
    
    return None

def parse_voice_command(text: str, output_channel: str = "slack", recipient_email: Optional[str] = None) -> Dict[str, Any]:
    payload = {
        "query": text,
        "top_k": parse_top_k(text),
        "output_channel": output_channel
    }
    salary_range = parse_salary_range(text)
    if salary_range:
        payload["salary_range"] = salary_range
    industry = parse_industry(text)
    if industry:
        payload["industry"] = industry
    location_filter = parse_location_filter(text)
    if location_filter:
        payload["location_filter"] = location_filter
    if recipient_email:
        payload["recipient_email"] = recipient_email
    return payload