import json
import os
import re
from dotenv import load_dotenv
from day2_python import clean_client_data

load_dotenv()

# High-Ticket dental procedures & canonical code alias map
HIGH_TICKET_PROCEDURES = [
    "Implants", "Invisalign", "Aligners", "Smile Makeover",
    "Full Mouth Rehab", "Root Canal", "Veneers", "Crown", "Braces"
]

PROCEDURE_SPECIALTY_TIER = {
    "Implants": {"category": "Implantology", "weight": 95},
    "Invisalign": {"category": "Orthodontics", "weight": 95},
    "Aligners": {"category": "Orthodontics", "weight": 90},
    "Smile Makeover": {"category": "Cosmetic", "weight": 90},
    "Full Mouth Rehab": {"category": "Prosthodontics", "weight": 100},
    "Root Canal": {"category": "Endodontics", "weight": 85},
    "Veneers": {"category": "Cosmetic", "weight": 85},
    "Crown": {"category": "Restorative", "weight": 80},
    "Braces": {"category": "Orthodontics", "weight": 80}
}

PROCEDURE_ALIAS_MAP = {
    "RCT": "Root Canal", "ROOT CANAL": "Root Canal",
    "IMP": "Implants", "IMPLANT": "Implants", "IMPLANTS": "Implants",
    "INVIS": "Invisalign", "INVISALIGN": "Invisalign",
    "ALIGN": "Aligners", "ALIGNERS": "Aligners",
    "FMR": "Full Mouth Rehab", "REHAB": "Full Mouth Rehab", "FULL MOUTH": "Full Mouth Rehab",
    "VENEER": "Veneers", "VENEERS": "Veneers",
    "CROWN": "Crown", "CROWNS": "Crown",
    "BRACES": "Braces", "SMILE": "Smile Makeover", "SMILE MAKEOVER": "Smile Makeover"
}

# Hospital Emergency Triage Keywords (Medical ESI Override)
EMERGENCY_MEDICAL_KEYWORDS = [
    "unconscious", "breathing difficulty", "cannot breathe", "chest pain",
    "severe trauma", "profuse bleeding", "uncontrollable bleeding", "facial fracture",
    "syncope", "fainted", "head injury", "choking"
]

URGENCY_KEYWORDS = [
    "asap", "urgent", "emergency", "immediately", "today", "pain", "severe", 
    "swelling", "bleeding", "toothache", "agony", "dard", "bohot", "bohut", 
    "jaldi", "khoon", "sojan", "dukh", "tention", "trouble"
]

BOOKING_INTENT_KEYWORDS = [
    "cost", "price", "quote", "fee", "fees", "package", "book", "appointment", 
    "schedule", "consultation", "availab", "slot", "emi", "finance", "kharcha", 
    "kitna", "kitne", "dam", "paisa", "paise", "rate", "chahiye", "karwana", "batao"
]

FINANCIAL_READINESS_KEYWORDS = [
    "cashless", "insurance", "policy", "tpa", "reimbursement", "star health",
    "hdfc ergo", "icici lombard", "corporate", "emi", "card", "cash", "ready to pay",
    "upfront", "finance"
]

NEGATIVE_INTENT_KEYWORDS = [
    "not interested", "dont want", "don't want", "nhi chahiye", "nahi chahiye",
    "cancel", "cancellation", "wrong number", "galat number", "galt number",
    "complaint", "bad service", "refund", "stop messaging", "unsubscribe",
    "too expensive", "bohot mahanga", "bohut mehenga"
]

# Pre-compiled Regex Patterns for High Performance (<0.1ms execution)
COMPILED_EMERGENCY = [re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE) for w in EMERGENCY_MEDICAL_KEYWORDS]
COMPILED_URGENCY = [re.compile(r"\b" + re.escape(w) + r"\b" if len(w) <= 4 else re.escape(w), re.IGNORECASE) for w in URGENCY_KEYWORDS]
COMPILED_FINANCIAL = [re.compile(re.escape(w), re.IGNORECASE) for w in FINANCIAL_READINESS_KEYWORDS]
COMPILED_NEGATIVE = [re.compile(re.escape(p), re.IGNORECASE) for p in NEGATIVE_INTENT_KEYWORDS]


def chinmay_lead_scorer(cleaned_data: dict) -> dict:
    """
    Hospital-Grade Enterprise Clinical & Revenue Triage Engine.
    Sub-millisecond execution using pre-compiled regex and multi-vector scoring:
    1. Clinical Emergency Risk Check (ESI Override / RED_CRITICAL)
    2. Revenue Priority & Specialty Tier
    3. Insurance & Financial Readiness Score
    4. Negative Signal & Opt-out Circuit
    """
    notes = cleaned_data.get("notes", "").lower()
    raw_proc_code = cleaned_data.get("procedure_code", "").upper().strip()

    # 1. Emergency Medical Check (ESI Level Override)
    matched_emergency = [w for w, rx in zip(EMERGENCY_MEDICAL_KEYWORDS, COMPILED_EMERGENCY) if rx.search(notes)]
    if matched_emergency:
        return {
            "intent_score": 100,
            "lead_tier": "RED_CRITICAL_EMERGENCY",
            "is_high_ticket": False,
            "matched_procedures": [],
            "urgency_signals": matched_emergency,
            "intent_signals": [],
            "financial_signals": [],
            "negative_signals": [],
            "reasoning": f"CRITICAL MEDICAL EMERGENCY DETECTED ({', '.join(matched_emergency)}). Immediate 112 / ER referral mandatory.",
            "evaluator": "Enterprise Hospital Clinical Triage Engine"
        }

    # 2. Procedure Detection & Specialty Classification
    matched_procedures = []
    if raw_proc_code in PROCEDURE_ALIAS_MAP:
        matched_procedures.append(PROCEDURE_ALIAS_MAP[raw_proc_code])
    for code, canonical in PROCEDURE_ALIAS_MAP.items():
        if code in raw_proc_code and canonical not in matched_procedures:
            matched_procedures.append(canonical)
    for proc in HIGH_TICKET_PROCEDURES:
        if re.search(r"\b" + re.escape(proc.lower()) + r"\b", notes) and proc not in matched_procedures:
            matched_procedures.append(proc)

    is_high_ticket = len(matched_procedures) > 0
    max_procedure_weight = max([PROCEDURE_SPECIALTY_TIER.get(p, {}).get("weight", 80) for p in matched_procedures], default=0)

    # 3. Extract Multi-Vector Signals
    matched_urgency = [w for w, rx in zip(URGENCY_KEYWORDS, COMPILED_URGENCY) if rx.search(notes)]
    matched_intent = [w for w in BOOKING_INTENT_KEYWORDS if w in notes]
    matched_financial = [w for w, rx in zip(FINANCIAL_READINESS_KEYWORDS, COMPILED_FINANCIAL) if rx.search(notes)]
    matched_negative = [p for p, rx in zip(NEGATIVE_INTENT_KEYWORDS, COMPILED_NEGATIVE) if rx.search(notes)]

    # 4. Enterprise Composite Scoring Matrix
    if is_high_ticket:
        base_score = max_procedure_weight - 10
    elif len(notes) > 10 or raw_proc_code:
        base_score = 35
    else:
        base_score = 20

    urgency_bonus = min(15, len(matched_urgency) * 10)
    intent_bonus = min(15, len(matched_intent) * 10)
    financial_bonus = min(10, len(matched_financial) * 5)
    negative_penalty = len(matched_negative) * 45

    final_score = max(1, min(100, base_score + urgency_bonus + intent_bonus + financial_bonus - negative_penalty))

    # 5. Hospital Triage Level Assignment
    if matched_negative or final_score < 30:
        lead_tier = "DISQUALIFIED"
    elif is_high_ticket and final_score >= 85:
        lead_tier = "VIP_HIGH_REVENUE"
    elif final_score >= 70:
        lead_tier = "URGENT_CLINICAL"
    elif final_score >= 40:
        lead_tier = "WARM_ELECTIVE"
    else:
        lead_tier = "COLD_ROUTINE"

    # 6. Rationale Construction
    rationale = [f"High-Ticket ({', '.join(matched_procedures)})" if is_high_ticket else "Standard Treatment Inquiry"]
    if matched_urgency:
        rationale.append(f"Urgency ({', '.join(matched_urgency)})")
    if matched_intent:
        rationale.append(f"Intent ({', '.join(matched_intent)})")
    if matched_financial:
        rationale.append(f"Financial Readiness ({', '.join(matched_financial)})")
    if matched_negative:
        rationale.append(f"Negative Signal ({', '.join(matched_negative)})")

    return {
        "intent_score": final_score,
        "lead_tier": lead_tier,
        "is_high_ticket": is_high_ticket,
        "matched_procedures": matched_procedures,
        "urgency_signals": matched_urgency,
        "intent_signals": matched_intent,
        "financial_signals": matched_financial,
        "negative_signals": matched_negative,
        "reasoning": f"{' + '.join(rationale)} Triage: {lead_tier}.",
        "evaluator": "Enterprise Hospital Clinical Triage Engine"
    }


def score_lead_intent(raw_patient_data: dict) -> dict:
    """Core Module: Cleans data and scores buying intent via Gemini API or Enterprise Fallback Engine."""
    cleaned_patient = clean_client_data(raw_patient_data)
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""You are an expert dental clinic triage assistant in Bengaluru.
Analyze the following patient intake data and evaluate buying intent & revenue priority.

Patient Data:
- Name: {cleaned_patient['name']}
- Procedure Code: {cleaned_patient['procedure_code']}
- Notes: {cleaned_patient['notes']}

High-Ticket Procedures List: {', '.join(HIGH_TICKET_PROCEDURES)}

Return ONLY a raw JSON object with the following fields:
{{
  "intent_score": <integer between 1 and 100>,
  "lead_tier": "<VIP_HIGH_REVENUE | URGENT_CLINICAL | WARM_ELECTIVE | COLD_ROUTINE | RED_CRITICAL_EMERGENCY | DISQUALIFIED>",
  "is_high_ticket": <boolean true/false>,
  "matched_procedures": [<list of matched high ticket procedures>],
  "reasoning": "<1-2 sentence explanation of the score>"
}}"""
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            clean_text = re.sub(r"^```[a-z]*\n?|\n?```$", "", response.text.strip())
            ai_result = json.loads(clean_text)
            ai_result["evaluator"] = "Gemini AI Engine"
            return {"patient": cleaned_patient, "triage": ai_result}
        except Exception as e:
            triage_result = chinmay_lead_scorer(cleaned_patient)
            err_msg = str(e).splitlines()[0]
            suffix = " (Gemini API rate/quota limit hit — using fallback engine)" if any(k in str(e) for k in ["429", "RESOURCE_EXHAUSTED"]) else f" (Gemini API fallback: {err_msg})"
            triage_result["reasoning"] += suffix
            return {"patient": cleaned_patient, "triage": triage_result}

    return {"patient": cleaned_patient, "triage": chinmay_lead_scorer(cleaned_patient)}


if __name__ == "__main__":
    print("==================================================")
    print("   ENTERPRISE HOSPITAL CLINICAL & REVENUE TRIAGE")
    print("==================================================\n")

    test_leads = [
        {
            "name": "   ananya roy ",
            "phone": "+91-99887 76655",
            "procedure_code": "  aligners ",
            "notes": " Hi, I am looking for full mouth Invisalign aligners treatment cost in Bengaluru. Have Star Health Insurance EMI option ready. Want to start ASAP. "
        },
        {
            "name": "vikram sethi",
            "phone": " 9876543210 ",
            "procedure_code": "CLEAN-01",
            "notes": "Do you offer routine teeth cleaning on Saturdays?"
        },
        {
            "name": "  kavita Sharma",
            "phone": "+91 9123456789",
            "procedure_code": "rct",
            "notes": "Severe toothache in my upper molar. Need root canal treatment urgently!"
        },
        {
            "name": "  Rohan Verma ",
            "phone": "98765 11223",
            "procedure_code": "implants",
            "notes": "Mera daant me bohot dard hai, dental implants ka kitna kharcha aayega? Cashless policy insurance details."
        },
        {
            "name": "Suresh Kumar",
            "phone": "9876500000",
            "procedure_code": "IMP",
            "notes": "Not interested in implants anymore, please cancel my appointment. Wrong number."
        },
        {
            "name": "Rajesh Hegde",
            "phone": "9900011122",
            "procedure_code": "EMERGENCY",
            "notes": "Patient fell down, profuse bleeding and unconscious. Urgent emergency!"
        }
    ]

    for idx, raw_lead in enumerate(test_leads, 1):
        print(f"--- TEST CASE {idx} ---")
        result = score_lead_intent(raw_lead)
        print(json.dumps(result, indent=2))
        print("\n")



