"""
intent.py
Fast intent detection — bypasses Groq for simple/common customer inputs.
Saves 40-50% of Groq token usage.
"""

INTENTS = {
    "yes_visit": {
        "patterns": [
            "aa jaunga", "aa jaungi", "aaonga", "aaunga", "aa sakta",
            "aa sakti", "aata hoon", "aati hoon", "visit karunga", "aaugi",
            "aa jaugi", "showroom aaunga", "showroom aaugi",
            "आ जाऊँगा", "आ जाऊँगी", "आ सकता", "आ सकती",
            "आता हूँ", "आती हूँ", "आ जाऊंगा", "आ जाऊंगी",
            "शोरूम आऊँगा", "शोरूम आऊँगी", "आऊँगा", "आऊँगी"
        ],
        "response": "Bahut accha ji! Main aapka intezaar karungi. Aap kab aa rahe hain — aaj ya kal?"
    },
    "acknowledgement": {
        "patterns": [
            "haan", "han", "haa", "ha", "ok", "okay", "theek", "theek hai",
            "ji haan", "bilkul", "sahi", "accha", "acha", "hmm", "hm",
            "हाँ", "हां", "ठीक है", "ठीक", "जी", "जी हाँ", "बिल्कुल",
            "सही", "अच्छा", "हम्म"
        ],
        "response": "Accha ji! Toh aap kab showroom aa sakte hain test ride ke liye?"
    },
    "busy": {
        "patterns": [
            "busy", "baad mein", "baad me", "abhi nahi", "abhi mat",
            "baad mein call", "later", "free nahi", "time nahi",
            "व्यस्त", "बाद में", "अभी नहीं", "बाद में कॉल", "फ्री नहीं",
            "टाइम नहीं", "अभी मत"
        ],
        "response": "Koi baat nahi ji! Main kab call karoon — aapko kab convenient rahega?"
    },
    "address": {
        "patterns": [
            "address", "kahan hai", "kahan he", "location", "showroom kahan",
            "jagah", "kidhar", "kahaan", "showroom ka", "showroom ki",
            "एड्रेस", "पता", "कहाँ है", "कहाँ", "कहां है", "कहां",
            "लोकेशन", "जगह", "किधर", "शोरूम कहाँ", "शोरूम का पता"
        ],
        "response": "Hamare showroom ka address hai — Lal Kothi, Tonk Road, Jaipur. Subah 9 baje se shaam 7 baje tak khula rehta hai!"
    },
    "timing": {
        "patterns": [
            "timing", "kitne baje", "kab khulta", "band kab", "working hours", 
            "khula", "showroom ka time", "showroom ki timing", "टाइम", "समय", 
            "कितने बजे", "कब खुलता", "बंद कब", "वर्किंग आवर्स", "खुला रहेगा", "शोरूम का टाइम", "शोरूम की टाइमिंग"
        ],
        "response": "Hamare showroom ki timing hai subah 9 baje se shaam 7 baje tak, Monday se Saturday."
    },
    "test_ride": {
        "patterns": [
            "test ride", "test drive", "chalana", "try", "chalake dekhna",
            "drive karna", "ride karna", "टेस्ट राइड", "टेस्ट ड्राइव", "चलाना", 
            "चला के देखना", "ड्राइव करना", "राइड करना", "चलाकर देखना"
        ],
        "response": "Bilkul ji! Test ride completely free hai, koi commitment nahi. Aap kab aa sakte hain?"
    },
    "not_interested": {
        "patterns": [
            "nahi chahiye", "interest nahi", "mat karo call", "band karo",
            "hata lo number", "nahi lena", "no thanks", "नहीं चाहिए", "इंटरेस्ट नहीं",
            "मत करो कॉल", "बंद करो", "हटा लो नंबर", "नहीं लेना", "कोई जरूरत नहीं",
            "zaroorat nahi", "जरूरत नहीं"
        ],
        "response": "Koi baat nahi ji! Kabhi bhi zaroorat ho toh call karein. Dhanyavaad!"
    },
    "callback": {
        "patterns": [
            "call karo", "call karna", "phone karo", "phone karna",
            "baad mein baat", "call back", "कॉल करो", "कॉल करना", 
            "फोन करो", "फोन करना", "बाद में बात", "कॉल बैक", "बाद में कॉल करो"
        ],
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
            if pattern in text_lower:
                print(f"[Intent] Matched '{intent_name}' for: '{text[:50]}'")
                return data["response"]

    return None