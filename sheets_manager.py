"""
sheets_manager.py
Google Sheets primary storage with local JSON fallback.
Tabs: Leads, Calls, Offers, Settings, Catalog, FAQ
"""
import json
import time
from datetime import datetime
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
import config

# ── LOCAL FALLBACK SETUP ──────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
LEADS_FILE   = DATA_DIR / "leads.json"
CALLS_FILE   = DATA_DIR / "calls.json"
OFFERS_FILE  = DATA_DIR / "offers.json"

# ── GOOGLE SHEETS SETUP ───────────────────────────────────────────────────────
_gc = None
_sheet = None

def _get_sheet():
    global _gc, _sheet
    if _sheet:
        return _sheet
    try:
        creds_dict = config.GOOGLE_CREDENTIALS
        if not creds_dict:
            print("[Sheets] No credentials found, using local JSON")
            return None
        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        _gc = gspread.authorize(creds)
        _sheet = _gc.open_by_key(config.GOOGLE_SHEET_ID)
        print("[Sheets] ✅ Connected to Google Sheets")
        return _sheet
    except Exception as e:
        print(f"[Sheets] ❌ Connection failed: {e}, using local JSON fallback")
        return None

def _get_tab(tab_name: str):
    sheet = _get_sheet()
    if not sheet:
        return None
    try:
        return sheet.worksheet(tab_name)
    except Exception as e:
        print(f"[Sheets] Tab '{tab_name}' not found: {e}")
        return None

# ── LOCAL HELPERS ─────────────────────────────────────────────────────────────
def _load(filepath: Path) -> list:
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save(filepath: Path, data: list):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def _rows_to_dicts(tab) -> list:
    """Convert gspread rows to list of dicts using first row as headers."""
    try:
        records = tab.get_all_records()
        return records
    except Exception as e:
        print(f"[Sheets] Read failed: {e}")
        return []

def _find_row(tab, key_col: str, key_val: str) -> tuple:
    """Find row index (1-based) and data for a matching key. Returns (row_idx, data)."""
    try:
        records = tab.get_all_records()
        headers = tab.row_values(1)
        col_idx = headers.index(key_col) + 1
        for i, record in enumerate(records):
            if str(record.get(key_col, "")) == str(key_val):
                return i + 2, record  # +2 because row 1 is header
        return None, None
    except Exception as e:
        print(f"[Sheets] Find row failed: {e}")
        return None, None

# ── LEADS ─────────────────────────────────────────────────────────────────────

def add_lead(lead: dict) -> str:
    lead_id = f"L{int(datetime.now().timestamp())}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    new_lead = {
        "lead_id":          lead_id,
        "name":             lead.get("name", ""),
        "mobile":           lead.get("mobile", ""),
        "interested_model": lead.get("interested_model", ""),
        "budget":           lead.get("budget", ""),
        "source":           lead.get("source", "manual"),
        "status":           "new",
        "temperature":      "warm",
        "assigned_to":      "",
        "assigned_mobile":  "",
        "call_count":       0,
        "last_called":      "",
        "next_followup":    "",
        "notes":            lead.get("notes", ""),
        "created_at":       now,
        "converted_at":     "",
        "tags":             lead.get("tags", ""),
    }

    # Try Google Sheets first
    tab = _get_tab("Leads")
    if tab:
        try:
            headers = tab.row_values(1)
            row = [str(new_lead.get(h, "")) for h in headers]
            tab.append_row(row)
            print(f"[Sheets] Lead {lead_id} added to Google Sheets")
        except Exception as e:
            print(f"[Sheets] Lead append failed: {e}, saving locally")
            _save_local_lead(new_lead)
    else:
        _save_local_lead(new_lead)

    return lead_id

def _save_local_lead(lead: dict):
    leads = _load(LEADS_FILE)
    leads.append(lead)
    _save(LEADS_FILE, leads)

def get_all_leads() -> list:
    tab = _get_tab("Leads")
    if tab:
        try:
            return _rows_to_dicts(tab)
        except Exception as e:
            print(f"[Sheets] get_all_leads failed: {e}, using local")
    return _load(LEADS_FILE)

def get_lead_by_mobile(mobile: str) -> dict | None:
    clean = mobile.replace("+91", "").replace(" ", "").strip()
    for r in get_all_leads():
        if str(r.get("mobile", "")).replace("+91", "").replace(" ", "").strip() == clean:
            return r
    return None

def get_lead_by_id(lead_id: str) -> dict | None:
    for r in get_all_leads():
        if str(r.get("lead_id", "")) == lead_id:
            return r
    return None

def update_lead(lead_id: str, updates: dict) -> bool:
    tab = _get_tab("Leads")
    if tab:
        try:
            row_idx, existing = _find_row(tab, "lead_id", lead_id)
            if row_idx:
                headers = tab.row_values(1)
                for key, val in updates.items():
                    if key in headers:
                        col_idx = headers.index(key) + 1
                        tab.update_cell(row_idx, col_idx, str(val))
                print(f"[Sheets] Lead {lead_id} updated")
                return True
        except Exception as e:
            print(f"[Sheets] update_lead failed: {e}, updating locally")

    # Local fallback
    leads = _load(LEADS_FILE)
    for lead in leads:
        if str(lead.get("lead_id", "")) == lead_id:
            lead.update(updates)
            _save(LEADS_FILE, leads)
            return True
    return False

def get_leads_due_for_followup() -> list:
    now = datetime.now()
    due = []
    for r in get_all_leads():
        if r.get("status") in ("dead", "converted"):
            continue
        nf = r.get("next_followup", "")
        if not nf:
            continue
        try:
            nf_dt = datetime.strptime(str(nf), "%Y-%m-%d %H:%M")
            if nf_dt <= now:
                due.append(r)
        except Exception:
            pass
    return due

def get_new_uncontacted_leads() -> list:
    return [r for r in get_all_leads() if r.get("status") == "new" and not r.get("last_called")]

# ── CALL LOG ──────────────────────────────────────────────────────────────────

def log_call(data: dict):
    log_id = f"C{int(datetime.now().timestamp())}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    record = {
        "log_id":       log_id,
        "lead_id":      data.get("lead_id", ""),
        "mobile":       data.get("mobile", ""),
        "direction":    data.get("direction", "outbound"),
        "duration_sec": data.get("duration_sec", 0),
        "status":       data.get("status", ""),
        "transcript":   data.get("transcript", "")[:1000],  # cap at 1000 chars
        "sentiment":    data.get("sentiment", "neutral"),
        "ai_summary":   data.get("ai_summary", ""),
        "next_action":  data.get("next_action", ""),
        "called_at":    now,
    }

    tab = _get_tab("Calls")
    if tab:
        try:
            headers = tab.row_values(1)
            row = [str(record.get(h, "")) for h in headers]
            tab.append_row(row)
            print(f"[Sheets] Call {log_id} logged to Google Sheets")
            return log_id
        except Exception as e:
            print(f"[Sheets] log_call failed: {e}, saving locally")

    calls = _load(CALLS_FILE)
    calls.append(record)
    _save(CALLS_FILE, calls)
    return log_id

# ── OFFERS ────────────────────────────────────────────────────────────────────

def get_active_offers() -> list:
    tab = _get_tab("Offers")
    if tab:
        try:
            offers = _rows_to_dicts(tab)
        except Exception:
            offers = _load(OFFERS_FILE)
    else:
        offers = _load(OFFERS_FILE)

    today = datetime.now().date()
    active = []
    for r in offers:
        vt = r.get("valid_till", "")
        try:
            if datetime.strptime(str(vt), "%Y-%m-%d").date() >= today:
                active.append(r)
        except Exception:
            active.append(r)
    return active

def add_offer(offer: dict) -> str:
    oid = f"O{int(datetime.now().timestamp())}"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    record = {
        "offer_id":    oid,
        "title":       offer.get("title", ""),
        "description": offer.get("description", ""),
        "valid_till":  offer.get("valid_till", ""),
        "models":      offer.get("models", ""),
        "uploaded_at": now,
    }

    tab = _get_tab("Offers")
    if tab:
        try:
            headers = tab.row_values(1)
            row = [str(record.get(h, "")) for h in headers]
            tab.append_row(row)
            return oid
        except Exception as e:
            print(f"[Sheets] add_offer failed: {e}, saving locally")

    offers = _load(OFFERS_FILE)
    offers.append(record)
    _save(OFFERS_FILE, offers)
    return oid

# ── CATALOG ───────────────────────────────────────────────────────────────────

def get_catalog() -> list:
    """Fetch bike catalog from Google Sheets Catalog tab."""
    tab = _get_tab("Catalog")
    if tab:
        try:
            return _rows_to_dicts(tab)
        except Exception as e:
            print(f"[Sheets] get_catalog failed: {e}")
    return []

# ── FAQ ───────────────────────────────────────────────────────────────────────

def get_faq() -> list:
    """Fetch FAQ entries from Google Sheets FAQ tab."""
    tab = _get_tab("FAQ")
    if tab:
        try:
            return _rows_to_dicts(tab)
        except Exception as e:
            print(f"[Sheets] get_faq failed: {e}")
    return []

# ── SETTINGS ──────────────────────────────────────────────────────────────────

SETTINGS_FILE = DATA_DIR / "settings.json"

def get_setting(key: str, default="") -> str:
    tab = _get_tab("Settings")
    if tab:
        try:
            records = _rows_to_dicts(tab)
            for r in records:
                if r.get("key") == key:
                    return str(r.get("value", ""))
        except Exception as e:
            print(f"[Sheets] get_setting failed: {e}")

    # Local fallback
    settings = _load(SETTINGS_FILE) if SETTINGS_FILE.exists() else []
    for r in settings:
        if r.get("key") == key:
            return str(r.get("value", ""))
    return default

def set_setting(key: str, value: str):
    tab = _get_tab("Settings")
    if tab:
        try:
            row_idx, existing = _find_row(tab, "key", key)
            if row_idx:
                tab.update_cell(row_idx, 2, str(value))
            else:
                tab.append_row([key, str(value)])
            return
        except Exception as e:
            print(f"[Sheets] set_setting failed: {e}")

    # Local fallback
    settings = _load(SETTINGS_FILE) if SETTINGS_FILE.exists() else []
    for r in settings:
        if r.get("key") == key:
            r["value"] = value
            _save(SETTINGS_FILE, settings)
            return
    settings.append({"key": key, "value": value})
    _save(SETTINGS_FILE, settings)