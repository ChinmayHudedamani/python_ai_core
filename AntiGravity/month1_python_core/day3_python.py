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

NEGATIVE_INTENT_KEYWORDS = [
    "not interested", "dont want", "don't want", "nhi chahiye", "nahi chahiye",
    "cancel", "cancellation", "wrong number", "galat number", "galt number",
    "complaint", "bad service", "refund", "stop messaging", "unsubscribe",
    "too expensive", "bohot mahanga", "bohut mehenga"
]


def chinmay_lead_scorer(cleaned_data: dict) -> dict:
    """Multi-Factor Fallback Lead Scorer & Tier Assigner."""
    notes = cleaned_data.get("notes", "").lower()
    raw_proc_code = cleaned_data.get("procedure_code", "").upper().strip()

    # 1. Procedure Detection
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

    # 2. Extract Signals
    matched_urgency = [
        w for w in URGENCY_KEYWORDS 
        if re.search(r"\b" + re.escape(w) + r"\b" if len(w) <= 4 else re.escape(w), notes)
    ]
    matched_intent = [w for w in BOOKING_INTENT_KEYWORDS if w in notes]
    matched_negative = [p for p in NEGATIVE_INTENT_KEYWORDS if p in notes]

    # 3. Dynamic Scoring & Tiering
    base_score = 75 if is_high_ticket else (35 if len(notes) > 10 or raw_proc_code else 20)
    urgency_points = min(15, len(matched_urgency) * 10)
    intent_points = min(15, len(matched_intent) * 10)
    negative_penalty = len(matched_negative) * 40

    final_score = max(1, min(100, base_score + urgency_points + intent_points - negative_penalty))

    if matched_negative or final_score < 30:
        lead_tier = "DISQUALIFIED"
    elif final_score >= 85:
        lead_tier = "HOT"
    elif final_score >= 60:
        lead_tier = "WARM"
    else:
        lead_tier = "COLD"

    # 4. Rationale Construction
    rationale_bits = [
        f"High-Ticket Procedure ({', '.join(matched_procedures)})" if is_high_ticket else "Standard Treatment Inquiry"
    ]
    if matched_urgency:
        rationale_bits.append(f"Urgency ({', '.join(matched_urgency)})")
    if matched_intent:
        rationale_bits.append(f"Booking Intent ({', '.join(matched_intent)})")
    if matched_negative:
        rationale_bits.append(f"Negative Signal ({', '.join(matched_negative)})")

    return {
        "intent_score": final_score,
        "lead_tier": lead_tier,
        "is_high_ticket": is_high_ticket,
        "matched_procedures": matched_procedures,
        "urgency_signals": matched_urgency,
        "intent_signals": matched_intent,
        "negative_signals": matched_negative,
        "reasoning": f"{' + '.join(rationale_bits)} Tier: {lead_tier}.",
        "evaluator": "Advanced Multi-Factor Fallback Engine"
    }


def score_lead_intent(raw_patient_data: dict) -> dict:
    """Core Module: Cleans data and scores buying intent via Gemini API or Fallback Engine."""
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
  "lead_tier": "<HOT | WARM | COLD | DISQUALIFIED>",
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
    print("   DAY 3: GEMINI API LEAD INTENT SCORER DEMO")
    print("==================================================\n")

    test_leads = [
        {
            "name": "   ananya roy ",
            "phone": "+91-99887 76655",
            "procedure_code": "  aligners ",
            "notes": " Hi, I am looking for full mouth Invisalign aligners treatment cost in Bengaluru. Want to start ASAP. "
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
            "notes": "Mera daant me bohot dard hai, dental implants ka kitna kharcha aayega? Jaldi appointment chahiye."
        },
        {
            "name": "Suresh Kumar",
            "phone": "9876500000",
            "procedure_code": "IMP",
            "notes": "Not interested in implants anymore, please cancel my appointment. Wrong number."
        }
    ]

    for idx, raw_lead in enumerate(test_leads, 1):
        print(f"--- TEST CASE {idx} ---")
        result = score_lead_intent(raw_lead)
        print(json.dumps(result, indent=2))
        print("\n")


