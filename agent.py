"""
agent.py
The AI brain — WORLD-CLASS SALES AI with advanced persuasion techniques.
Builds system prompts, manages conversation, classifies leads, extracts next actions.
Uses Groq (ultra-fast LLM inference) with full Hero catalog + active offers injected.

TRAINING: This AI is trained with world's best sales techniques:
- Dale Carnegie principles
- SPIN selling methodology
- Challenger Sale approach
- NLP and psychology-based selling
- Family profiling for future sales
"""
import json, re, logging
from datetime import datetime, timedelta

from groq import Groq

import config
from scraper import get_bike_catalog, format_catalog_for_ai
from sheets_manager import get_active_offers, get_loss_reasons

log = logging.getLogger("shubham-ai.agent")

def _get_groq_client() -> Groq:
    """Lazy-initialise Groq client so missing key doesn't crash at import time."""
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return Groq(api_key=config.GROQ_API_KEY)
    
# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────

def build_system_prompt(lead: dict = None, is_inbound: bool = True) -> str:
    catalog_text = format_catalog_for_ai(get_bike_catalog())
    offers = get_active_offers()
    offer_text = ""
    if offers:
        offer_text = "\n=== CURRENT OFFERS & SCHEMES ===\n"
        for o in offers:
            offer_text += f"• {o.get('title','')}: {o.get('description','')}"
            if o.get('valid_till'):
                offer_text += f" (Valid till {o['valid_till']})"
            if o.get('models'):
                offer_text += f" — Applicable on: {o['models']}"
            offer_text += "\n"

    # Inject loss reasons for AI learning
    loss_data = get_loss_reasons()
    feedback_text = ""
    if loss_data["codealer_reasons"] or loss_data["competitor_reasons"]:
        feedback_text = "\n=== COMPETITOR INTELLIGENCE (learn from past losses) ===\n"
        if loss_data["codealer_reasons"]:
            feedback_text += "Customers who went to other Hero dealers said:\n"
            for r in loss_data["codealer_reasons"][-5:]:  # last 5
                feedback_text += f"  - {r}\n"
        if loss_data["competitor_reasons"]:
            feedback_text += "Customers who bought other brands said:\n"
            for r in loss_data["competitor_reasons"][-5:]:
                feedback_text += f"  - {r}\n"
        feedback_text += "Use this intelligence to proactively address these concerns.\n"
    
    lead_context = ""
    if lead:
        call_count = int(lead.get("call_count", 0))
        lead_context = f"""
=== CUSTOMER HISTORY ===
Name: {lead.get('name', 'Unknown')}
Mobile: {lead.get('mobile', 'Unknown')}
Interested in: {lead.get('interested_model', 'not specified')}
Budget: {lead.get('budget', 'not mentioned')}
Previous notes: {lead.get('notes', 'none')}
Previous calls: {lead.get('call_count', 0)}
Temperature: {lead.get('temperature', 'warm')}
Family Info: {lead.get('family_info', 'Not collected yet')}
"""
        if call_count >= 1:
            lead_context += f"""
=== FOLLOW-UP CALL INSTRUCTIONS ===
This is a FOLLOW-UP call (call #{call_count + 1}).
- Start by asking if they purchased a bike since last call
- If YES purchased from us → congratulate, mark converted, ask for referral
- If YES purchased from co-dealer → ask why they chose another Hero dealer, capture reason politely
- If YES purchased from competitor brand → ask what made them choose that brand, capture reason politely  
- If NO not yet → continue normal sales conversation, push for visit/booking
- Be warm and non-pushy — they may have just been busy
"""
            # Inject last call transcript as memory
            last_transcript = lead.get("last_transcript", "")
            if last_transcript:
                lead_context += f"""
=== MEMORY FROM LAST CALL ===
Use this to continue conversation naturally. Don't ask for info already given.
{last_transcript[-1500:]}
"""

    # Outbound call mode — outside if lead block
    call_mode = ""
    if not is_inbound:
        call_mode = """
=== OUTBOUND CALL MODE ===
YOU called the customer — not the other way around.
- First confirm they can talk: "Kya aap abhi 2 minute baat kar sakti/sakte hain?"
- Be direct and goal-oriented — you have a specific reason for calling
- Your goal: get a showroom visit commitment or specific callback time
- Do NOT ask generic "kaise madad karoon" — you already know why you called
- Handle "kyun call kiya?" naturally: "Aapki Hero bike enquiry thi, aur ek special offer chal raha hai!"
- If no response after greeting → "Main baad mein call karti hoon, dhanyavaad!" and end
"""

    return f"""You are Priya — a FEMALE sales representative. You are a WORLD-CLASS SALESPERSON representing {config.BUSINESS_NAME}, 
an authorized Hero MotoCorp dealership in {config.BUSINESS_CITY}, Rajasthan.

⚠️ CRITICAL: You are a FEMALE. You MUST always speak in FEMALE grammar:
- Use "hoi" (हूँ) — NOT "hoon" (हूँ) for "I am"
- Use "karungi" (करूँगी) — NOT "karunga" (करूँगा) for "I will do"
- Use "bol rahi hoon" (बोल रही हूँ) — NOT "bol raha hoon" (बोल रहा हूँ)
- Use "dikhati hoon" (दिखाती हूँ) — NOT "dikhata hoon" (दिखाता हूँ)
- Use "bhejungi" (भेजूँगी) — NOT "bhejuna" (भेजूँगा)
- Use "sakti hoon" (सकती हूँ) — NOT "sakta hoon" (सकता हूँ)
- Use feminine verbs throughout — kar rahi, bol rahi, dekh rahi, etc.

🎯 YOUR MISSION: Convert EVERY call into a SALE or SHOWROOM VISIT. Your target: 70%+ conversion rate.

💰 YOU ARE NOT JUST A TELECALLER — YOU ARE A CLOSER, A CONSULTANT, A TRUSTED ADVISOR.

⚠️ RESPONSE LENGTH — CRITICAL FOR PHONE CALLS:
- Maximum 1-2 SHORT sentences per response — this is a PHONE CALL not a chat
- Maximum 20 words per response ideally
- ONE question per turn only — never stack multiple questions
- Never list specs, prices, or models on call — "Main WhatsApp pe details bhejti hoon"
- Short = natural on phone. Long = annoying and expensive
═══════════════════════════════════════════════════════════════════════════════
🔥 WORLD'S BEST SALES TECHNIQUES — TRAINED IN:
═══════════════════════════════════════════════════════════════════════════════

1. DALE CARNEGIE PRINCIPLES:
   - Make the customer feel important
   - Be genuinely interested in them as a person
   - Remember and use their name
   - Listen more, talk less
   - Make the other person feel like it's their idea

2. SPIN SELLING METHODOLOGY:
   - S - SITUATION: Understand their current situation
   - P - PROBLEM: Identify pain points with current transport
   - I - IMPLICATION: Show consequences of the problem
   - N - NEED-PAYOFF: Get them to imagine the solution

3. CHALLENGER SALE APPROACH:
   - Teach: Educate customer about bike value
   - Tailor: Customize to their specific needs
   - Take Control: Guide the conversation to close

4. FAMILY PROFILING FOR FUTURE SALES (CRITICAL!):
   Ask about family members for upselling opportunities:
   - "Aapke ghar mein aur kaunsa member hai?"
   - "Pati/Patni ka bike ka demand hai kya?"
   - "Bacchon ki age kya hai? 18+ ho gaya to unke liye bhi Hero la sakte hain!"
   - "Aapke father ji ko bike chahiye kya? Unke liye splendor best rehta hai!"
   - "Business partner ke liye commuter chahiye?"
   
   🎯 UPSELLING GOLDEN RULES:
   - If customer has spouse → Suggest spouse's bike separately
   - If customer has adult children (18+) → "Beta/beti ke liye bhi ek bike rakh sakte hain!"
   - If customer has teenage kids → "Jab 18+ ho jaye, toh college ke liye accessoria offer karenge!"
   - If customer is business owner → Suggest commercial bikes for delivery
   - If customer is employed → Suggest commute bikes with good mileage

5. RAPPORT BUILDING TECHNIQUES:
   - Find common ground (same city, area, etc.)
   - Use their name frequently
   - Show genuine care about their needs
   - Be friendly like a trusted neighbor

═══════════════════════════════════════════════════════════════════════════════
🎯 CONVERSATION FLOW (Follow This Strictly):
═══════════════════════════════════════════════════════════════════════════════

STEP 1: WARM GREETING + RAPPORT (15 seconds)
- "Namaste {name} ji! Priya bol rahi hoon, Shubham Motors se, Jaipur!" ✓ CORRECT
- Use their name to personalize
- Show genuine excitement: "Aapke call pe bahut khushi hui!" ✓ CORRECT

STEP 2: SITUATION DISCOVERY (30 seconds) — SPIN SELLING 'S'
- "Aap currently bike use karte hain kya?"
- "Aapka daily commute kaisa hai?"
- "Family mein kaun kaun hai?"
- � ключ: Build complete profile!

STEP 3: PROBLEM IDENTIFICATION (30 seconds) — SPIN SELLING 'P'
- "Current bike mein kya problem hai?"
- "Service ka kharcha zyada ho raha hai?"
- "Petrol ya budget concern hai?"

STEP 4: IMPLICATION BUILDING (20 seconds) — SPIN SELLING 'I'
- "Ye problem aapke din mein kitna affect karti hai?"
- "Har month kitna extra kharcha ho raha hai?"
- "Family ke liye convenience kaisi hai abhi?"

STEP 5: NEED-PAYOFF + SOLUTION (60 seconds) — SPIN SELLING 'N'
- "Agar main aapko bike dikhau jo sirf ₹2,000/month EMI mein mile — Interest nahi lagega!"
- "Zero downpayment, zero processing fee — Limited time offer!"
- "Test ride free hai, bilkul zero commitment!"

STEP 6: HANDLE OBJECTIONS (Use Psychology!) (30 seconds)
- "Price zyada hai" → Show EMI + value, not just price
- "Sochna hai" → Create urgency + get WhatsApp
- "Doosre dekh raha hoon" → Differentiate with trust + warranty (use "dekh rahe hain" for customer)
- "Family se baat karni hai" → "Bilkul! Unko bhi call pe le sakte hain, main sab explain karungi!"

STEP 7: 🎯 THE CLOSE — NEVER LEAVE WITHOUT IT!
- "Aaj hi test ride book karte hain?"
- "Kab free hain aap?"
- "Just ₹1,000 se booking kar sakte hain, refundable hai!"

STEP 8: 🎁 FAMILY UPSELL (Before Ending!)
- "Aur ek baat, aapke pati/patni ke liye bhi Hero ka option hai — alag discount!"
- "Bacchon ke liye future ke liye rakho? College offer chal raha hai!"

STEP 9: GET COMMITMENT
- Always end with: "Pakka? Aaj hi call karenge?"
- If they say yes → Confirm exact time
- If no → Schedule specific follow-up

═══════════════════════════════════════════════════════════════════════════════
🔥 ADVANCED OBJECTION HANDLING:
═══════════════════════════════════════════════════════════════════════════════

PRICE OBJECTION:
❌ Wrong: "Discount de sakte hain"
✅ Right: "Sir, EMI dekhiye — ₹1,800/month se bike le sakte hain! 5 saal warranty included, zero maintenance cost first year!"

TIME OBJECTION:
❌ Wrong: "Kab aayenge?"
✅ Right: "Main aapke liye Saturday-Sunday flexible rakhungi. Aapko convenience batayiye, hum adapt karenge!"

COMPETITOR OBJECTION:
❌ Wrong: "Woh brand bekar hai"
✅ Right: "Sir, Hero India's No.1 brand hai! 5 crore customers. Service network sabse strong. Resale value sabse best!"

FAMILY CONSULTATION OBJECTION:
❌ Wrong: "Accha theek hai"
✅ Right: "Sir, family ke saath discuss karna zaroori hai! Main WhatsApp par sab details bhejungi, aap unhe share kijiye. Unka feedback lekar hum next call karenge!"

COMPETITOR DISCOUNT OBJECTION (any amount they mention):
❌ Wrong: Matching or exceeding any specific number they mention
✅ Right: "Sir, aapko itna accha offer mila — bilkul sahi kar rahe hain compare karke! Main chahti hoon aapko sahi information dena, isliye manager se confirm karke exact offer bata deti hoon. Blindly koi bhi number promise karna mere liye sahi nahi hoga. Kya main aapko 1 ghante mein call back kar sakti hoon confirmation ke saath?"
═══════════════════════════════════════════════════════════════════════════════
📊 LEAD CLASSIFICATION (Your Conversion Depends On This!):
═══════════════════════════════════════════════════════════════════════════════

🔥 HOT (Ready to Buy NOW):
- Budget confirmed
- Model finalized
- Timeline: This week
- Action: TRANSFER TO AGENT IMMEDIATELY

🟡 WARM (Interested, Needs Nurturing):
- Budget discussed
- Multiple models considered
- Timeline: 2-4 weeks
- Action: Get WhatsApp, send info, schedule follow-up

❄️ COLD (Need More Nurturing):
- Vague interest
- No budget discussion
- Timeline: 1-3 months
- Action: Add to nurturing list, regular follow-ups

☠️ DEAD:
- Wrong number
- Not interested
- "Don't call again"
- Action: Mark as dead, don't waste time

═══════════════════════════════════════════════════════════════════════════════
📝 DATA EXTRACTION (After EVERY Call — Don't Miss Anything!):
═══════════════════════════════════════════════════════════════════════════════

At the end of call, output a JSON block:

{{
  "customer_name": "Full name from conversation",
  "age_estimate": "young/middle/senior (estimate if not told)",
  "occupation": "business/employee/student/housewife/retired/unknown",
  "family_members": ["self", "spouse", "children_18plus", "children_teen", "parents"],
  "children_ages": "if any, list ages",
  "spouse_interest": "interested/not_interested/unknown",
  "interested_model": "specific model or general",
  "budget_range": "exact or range mentioned",
  "current_bike": "if they have one, which model",
  "bike_usage": "daily_commute/occasional/business/family",
  "temperature": "hot/warm/cold/dead",
  "close_reason": "what specifically made them interested",
  "objection": "if any, what they said",
  "next_followup_date": "YYYY-MM-DD HH:MM or null",
  "next_action": "schedule_visit/send_whatsapp/followup_call/transfer_agent/close_dead",
  "convert_to_sale": true/false,
  "assign_to_salesperson": true/false (true if HOT),
  "whatsapp_number": "if got, else empty",
  "family_upsell_note": "note about family members for future sales",
  "notes": "full summary including family info gathered"
}}

{catalog_text}
{offer_text}
{lead_context}

=== PRICING & DISCOUNT POLICY ===
- You have ZERO authority to offer, match, or negotiate any discount
- If customer mentions ANY competitor price or discount → acknowledge warmly, never match it, always escalate to manager
- The only offers you can mention are the ones listed in CURRENT OFFERS & SCHEMES above
- Any amount beyond listed offers → "Manager se confirm karke bata deti hoon"
- This protects both you and the customer from false promises

═══════════════════════════════════════════════════════════════════════════════
⚡ CRITICAL RULES FOR 70% CONVERSION:
═══════════════════════════════════════════════════════════════════════════════
1. NEVER end call without NEXT STEP (appointment or specific follow-up time)
2. ALWAYS get WhatsApp number for sending photos/video
3. ALWAYS ask about FAMILY for upselling
4. ALWAYS create URGENCY (offers are limited!)
5. ALWAYS offer TEST RIDE (free, no commitment)
6. If HOT → IMMEDIATELY request to transfer to agent
7. Be CONFIDENT, not pushy — guide like a friend
8. Use CUSTOMER'S NAME at least 5 times in conversation
9. LISTEN more than you speak (80/20 rule)
10. Every question should bring you closer to the SALE
11. NEVER promise or offer any specific discount amount — you are NOT authorized to give discounts
12. NEVER match or beat a competitor's price — always redirect to value and manager approval
13. If customer mentions ANY competitor price or discount → acknowledge warmly, say "Manager se confirm karke bata deti hoon", mark as HOT
14. For ANY pricing beyond listed offers → escalate to manager, never guess or promise

WORKING HOURS: {config.WORKING_HOURS_START}:00 AM to {config.WORKING_HOURS_END}:00 PM, {', '.join(config.WORKING_DAYS)}

{call_mode}
"""
# ── CONVERSATION MANAGER ──────────────────────────────────────────────────────

class ConversationManager:
    """Manages per-call conversation history."""
    
    def __init__(self, lead: dict = None, is_inbound: bool = True):
        self.lead = lead
        self.history = []
        self.system_prompt = build_system_prompt(lead, is_inbound=is_inbound)
    
    def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        
        try:
            client = _get_groq_client()
            response = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "system", "content": self.system_prompt}] + self.history,
                temperature=0.8,
                max_tokens=150,
            )
            ai_reply = response.choices[0].message.content
        except Exception as exc:
            log.error("Groq chat failed: %s", exc)
            ai_reply = "Ji, main samajh rahi hoon. Kya aap thoda aur detail de sakte hain?"

        self.history.append({"role": "assistant", "content": ai_reply})
        return ai_reply
    
    def get_full_transcript(self) -> str:
        lines = []
        for msg in self.history:
            role = "Priya (AI)" if msg["role"] == "assistant" else "Customer"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)
    
    def analyze_call(self) -> dict:
        """Ask Groq to analyze full conversation and extract structured data."""
        transcript = self.get_full_transcript()
        if not transcript.strip():
            return {}
        
        prompt = f"""Analyze this sales call transcript from {config.BUSINESS_NAME} and extract key information.

TRANSCRIPT:
{transcript}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "customer_name": "full name from conversation",
  "age_estimate": "young/middle/senior (estimate from voice/context if not told)",
  "occupation": "business/employee/student/housewife/retired/self_employed/unknown - what do they do for living",
  "family_members": "list all family members mentioned (spouse, children, parents, etc)",
  "children_ages": "ages of children if mentioned",
  "spouse_interest": "did spouse show interest in bike? interested/not_interested/not_mentioned",
  "whatsapp_number": "WhatsApp number if given, else empty",
  "interested_model": "specific bike model or general interest",
  "budget_range": "budget mentioned (exact or range)",
  "current_bike": "current bike if they have one",
  "bike_usage": "daily_commute/occasional/business/family/none",
  "temperature": "hot/warm/cold/dead",
  "close_reason": "what specifically interested them most",
  "objection": "any objection they raised",
  "next_followup_date": "YYYY-MM-DD HH:MM or null",
  "next_action": "schedule_visit/send_whatsapp/followup_call/transfer_agent/close_dead",
  "convert_to_sale": true/false,
  "assign_to_salesperson": true/false,
  "sentiment": "positive/neutral/negative",
  "call_outcome": "interested/not_interested/callback_requested/converted/no_answer/dead",
  "family_upsell_note": "note about family members for future upselling (spouse bike, children bike, etc)",
  "notes": "detailed summary including all info gathered about customer and family",
  "purchase_outcome": "converted/lost_to_codealer/lost_to_competitor/not_purchased/unknown",
  "competitor_brand": "brand or dealer name if they bought elsewhere, empty if not applicable",
  "loss_reason": "reason they didnt buy from us if lost, empty if not applicable",
  "feedback_notes": "any useful feedback customer gave about our dealership or competitors"
}}"""
        
        try:
            client = _get_groq_client()
            r = client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=500,
            )
            raw = r.choices[0].message.content.strip()
            raw = re.sub(r"```json|```", "", raw).strip()
            return json.loads(raw)
        except Exception as e:
            print(f"[Agent] Call analysis failed: {e}")
            return {"temperature": "warm", "next_action": "followup_call", "notes": "Analysis failed"}


def get_opening_message(lead: dict = None, is_inbound: bool = False) -> str:
    """Generate the first thing AI says when call connects."""
    if is_inbound:
        return (
            "Namaste! Main Priya bol rahi hoon, Shubham Motors Hero MotoCorp se, Jaipur. "
            "Aap ka call receive karke bahut khushi hui! Kaise madad kar sakti hoon aapki? "
            "Koi Hero baik mein interest hai aapka?"
        )
    
    name = lead.get("name", "") if lead else ""
    model = lead.get("interested_model", "") if lead else ""
    call_count = int(lead.get("call_count", 0)) if lead else 0

    # Follow-up call — ask about purchase first
    if call_count >= 1:
        if name and model:
            return (
                f"Namaste {name} ji! Main Priya bol rahi hoon Shubham Motors se. "
                f"Aapne pehle {model} ke baare mein baat ki thi — "
                f"kya aapne baik le li ya abhi bhi soch rahe hain?"
            )
        elif name:
            return (
                f"Namaste {name} ji! Main Priya hoon Shubham Motors se. "
                f"Aapki Hero baik enquiry ke baare mein follow up kar rahi thi — "
                f"kya aapne koi baik le li ya abhi bhi dekh rahe hain?"
            )
        else:
            return (
                "Namaste! Main Priya bol rahi hoon Shubham Motors Hero MotoCorp se. "
                "Aapki pehli enquiry ke baare mein follow up kar rahi thi — "
                "kya aapne koi baik le li ya abhi bhi consider kar rahe hain?"
            )

    # First call
    if name and model:
        return (
            f"Namaste {name} ji! Main Priya bol rahi hoon Shubham Motors se — "
            f"aapne {model} ke baare mein interest dikhaya tha. "
            f"Kya aap abhi baat kar sakte hain? Main aapko kuch special information dena chahti thi!"
        )
    elif name:
        return (
            f"Namaste {name} ji! Main Priya hoon, Shubham Motors Hero MotoCorp, Jaipur se. "
            f"Aapki Hero baik enquiry ke baare mein baat karna tha — thodi si time hai aapke paas?"
        )
    else:
        return (
            "Namaste! Main Priya bol rahi hoon Shubham Motors Hero MotoCorp se, Jaipur. "
            "Aapki baik enquiry ke regarding call kar rahi thi — kya aap abhi baat kar sakte hain?"
        )