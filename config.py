import os, json
from dotenv import load_dotenv

load_dotenv()

# Exotel credentials
EXOTEL_API_KEY      = os.getenv("EXOTEL_API_KEY", "")
EXOTEL_API_TOKEN    = os.getenv("EXOTEL_API_TOKEN", "")
EXOTEL_ACCOUNT_SID  = os.getenv("EXOTEL_ACCOUNT_SID", "shubhammotors1")
EXOTEL_PHONE_NUMBER = os.getenv("EXOTEL_PHONE_NUMBER", "+919513886363")
EXOTEL_SUBDOMAIN    = os.getenv("EXOTEL_SUBDOMAIN", "api.exotel.com")

# Twilio credentials
TWILIO_ACCOUNT_SID  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+12173973537")

# AI / TTS / STT keys
GROQ_API_KEY        = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL          = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DEEPGRAM_API_KEY    = os.getenv("DEEPGRAM_API_KEY", "")
SARVAM_API_KEY      = os.getenv("SARVAM_API_KEY", "")
NGROK_AUTH_TOKEN    = os.getenv("NGROK_AUTH_TOKEN", "")

# Google Sheets
GOOGLE_SHEET_ID     = os.getenv("GOOGLE_SHEET_ID", "")
try:
    GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON", "{}"))
except Exception:
    GOOGLE_CREDENTIALS = {}

# Business info
BUSINESS_NAME       = os.getenv("BUSINESS_NAME", "Shubham Motors")
BUSINESS_CITY       = os.getenv("BUSINESS_CITY", "Jaipur")
WEBSITE_URL         = os.getenv("WEBSITE_URL", "")

# Work hours
WORKING_HOURS_START = int(os.getenv("WORKING_HOURS_START", "9"))
WORKING_HOURS_END   = int(os.getenv("WORKING_HOURS_END", "19"))
WORKING_DAYS        = os.getenv(
    "WORKING_DAYS",
    "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday"
).split(",")

# Sales team
SALES_TEAM = []
for _i in range(1, 6):
    _n = os.getenv(f"SALESPERSON_{_i}_NAME")
    _m = os.getenv(f"SALESPERSON_{_i}_MOBILE")
    if _n and _m:
        SALES_TEAM.append({"name": _n, "mobile": _m})

# Defaults
MAX_FOLLOWUP_ATTEMPTS   = int(os.getenv("MAX_FOLLOWUP_ATTEMPTS", "3"))
DEFAULT_FOLLOWUP_TIME   = os.getenv("DEFAULT_FOLLOWUP_TIME", "10:00")
DEFAULT_LANGUAGE        = os.getenv("DEFAULT_LANGUAGE", "hinglish")
SILENCE_TIMEOUT_SECONDS = int(os.getenv("SILENCE_TIMEOUT_SECONDS", "5"))
PUBLIC_URL              = os.getenv("PUBLIC_URL", "http://localhost:5000")
PORT                    = int(os.getenv("PORT", "5000"))