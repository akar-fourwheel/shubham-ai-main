"""
intent.py
Fast intent detection — bypasses Groq for simple/common customer inputs.
Saves 40-50% of Groq token usage.
"""
import re

INTENTS = {
    "acknowledgement": {
        "patterns": ["haan", "han", "haa", "ha", "ok", "okay", "theek", "theek hai", 
                     "ji", "ji haan", "bilkul", "sahi", "accha", "acha", "hmm", "hm"],
        "response": "Accha ji! Toh aap kab showroom aa sakte hain test ride ke liye?"
    },
    "busy": {
        "patterns": ["busy", "baad mein", "baad me", "abhi nahi", "abhi mat", 
                     "baad mein call", "later", "free nahi", "time nahi"],
        "response": "Koi baat nahi ji! Main kab call karoon — aapko kab convenient rahega?"
    },
    "address": {
        "patterns": ["address", "kahan hai", "kahan he", "location", "showroom kahan", 
                     "jagah", "kidhar", "kahaan"],
        "response": "Hamare showroom ka address hai — Lal Kothi, Tonk Road, Jaipur. Subah 9 baje se shaam 7 baje tak khula rehta hai!"
    },
    "timing": {
        "patterns": ["timing", "time", "kitne baje", "kab khulta", "band kab", 
                     "working hours", "khula"],
        "response": "Hamare showroom ki timing hai subah 9 baje se shaam 7 baje tak, Monday se Saturday."
    },
    "test_ride": {
        "patterns": ["test ride", "test drive", "chalana", "try", "chalake dekhna", 
                     "drive karna", "ride karna"],
        "response": "Bilkul ji! Test ride completely free hai, koi commitment nahi. Aap kab aa sakte hain?"
    },
    "yes_visit": {
        "patterns": ["aa jaunga", "aa jaungi", "aaonga", "aaunga", "aa sakta", 
                     "aa sakti", "aata hoon", "aati hoon", "visit karunga", "aaugi"],
        "response": "Bahut accha ji! Main aapka intezaar karungi. Aap kab aa rahe hain — aaj ya kal?"
    },
    "not_interested": {
        "patterns": ["nahi chahiye", "interest nahi", "mat karo call", "band karo", 
                     "hata lo number", "nahi lena", "no thanks"],
        "response": "Koi baat nahi ji! Kabhi bhi zaroorat ho toh call karein. Dhanyavaad!"
    },
    "callback": {
        "patterns": ["call karo", "call karna", "phone karo", "phone karna", 
                     "baad mein baat", "call back"],
        "response": "Bilkul ji! Main aapko call karungi. Kab convenient rahega aapko — subah ya shaam?"
    }
}

def detect_intent(text: str) -> str | None:
    """
    Check if customer input matches a known intent.
    Returns fixed response string if matched, None if should go to Groq.
    """
    text_lower = text.lower().strip()
    
    # Skip very short noise
    if len(text_lower) < 2:
        return None
    
    for intent_name, data in INTENTS.items():
        for pattern in data["patterns"]:
            # Exact match or contained in text
            if pattern == text_lower or re.search(rf"\b{re.escape(pattern)}\b", text_lower):
                print(f"[Intent] Matched '{intent_name}' for: '{text[:50]}'")
                return data["response"]
    
    return None