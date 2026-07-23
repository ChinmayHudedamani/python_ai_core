import json
import os
import re
from dotenv import load_dotenv
from day2_python import clean_client_data

# Load environment variables from .env file
load_dotenv()

# High-Ticket dental procedures specified in Project Spec (Module C)
HIGH_TICKET_PROCEDURES = [
    "Implants",
    "Invisalign",
    "Aligners",
    "Smile Makeover",
    "Full Mouth Rehab",
    "Root Canal",
    "Veneers",
    "Crown",
    "Braces"
]

URGENCY_KEYWORDS = [
    # English
    "asap", "urgent", "emergency", "immediately", "today", 
    "pain", "severe", "swelling", "bleeding", "toothache",
    # Hinglish / Local
    "dard", "bohot", "bohut", "jaldi", "khoon", "sojan", "dukh", "tention"
]

BOOKING_INTENT_KEYWORDS = [
    # English
    "cost", "price", "quote", "fee", "fees", "package", 
    "book", "appointment", "schedule", "consultation", "availab",
    # Hinglish / Local
    "kharcha", "kitna", "kitne", "dam", "paisa", "paise", "rate", "chahiye", "karwana"
]


def heuristic_lead_scorer(cleaned_data: dict) -> dict:
    """
    Enhanced Rule-Based Scorer (Fallback Engine).
    Multi-factor evaluation:
    1. High-Ticket Procedure matching (procedure_code & notes regex)
    2. Urgency & Pain detection
    3. Financial / Booking intent detection
    Calculates a weighted intent score (1-100) with detailed rationale.
    """
    notes = cleaned_data.get("notes", "").lower()
    proc_code = cleaned_data.get("procedure_code", "").upper()

    # 1. Procedure Detection
    matched_procedures = []
    for proc in HIGH_TICKET_PROCEDURES:
        pattern = r"\b" + re.escape(proc.lower()) + r"\b"
        if re.search(pattern, notes) or proc.upper() in proc_code or proc.lower() in notes:
            if proc not in matched_procedures:
                matched_procedures.append(proc)

    is_high_ticket = len(matched_procedures) > 0

    # 2. Urgency Detection
    matched_urgency = [
        word for word in URGENCY_KEYWORDS 
        if re.search(r"\b" + re.escape(word) + r"\b", notes)
    ]
    has_urgency = len(matched_urgency) > 0

    # 3. Booking / Price Intent Detection
    matched_intent = [
        word for word in BOOKING_INTENT_KEYWORDS 
        if word in notes
    ]
    has_intent = len(matched_intent) > 0

    # 4. Score Calculation & Tier Assignment
    if is_high_ticket:
        if has_urgency and has_intent:
            score = 98
        elif has_urgency or has_intent:
            score = 92
        else:
            score = 85
        rationale_bits = [f"High-Ticket Procedure ({', '.join(matched_procedures)})"]
    else:
        if has_urgency and has_intent:
            score = 80
        elif has_urgency:
            score = 75
        elif has_intent:
            score = 65
        elif len(notes) > 10:
            score = 45
        else:
            score = 25
        rationale_bits = ["Standard Treatment Inquiry"]

    if matched_urgency:
        rationale_bits.append(f"Urgency Signal ({', '.join(matched_urgency)})")
    if matched_intent:
        rationale_bits.append(f"Booking/Price Intent ({', '.join(matched_intent)})")

    reasoning = " + ".join(rationale_bits) + "."

    return {
        "intent_score": score,
        "is_high_ticket": is_high_ticket,
        "matched_procedures": matched_procedures,
        "urgency_signals": matched_urgency,
        "intent_signals": matched_intent,
        "reasoning": reasoning,
        "evaluator": "Advanced Rule-Based Fallback Engine"
    }


def score_lead_intent(raw_patient_data: dict) -> dict:
    """
    Day 3 Core Module: Evaluates patient intake data and returns an intent score (1-100),
    high-ticket classification, and routing decision.
    """
    # Step 1: Clean data using Day 2 Intake Valve
    cleaned_patient = clean_client_data(raw_patient_data)

    api_key = os.environ.get("GEMINI_API_KEY")

    # Step 2: Attempt Gemini API scoring if API key is present
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            prompt = f"""
You are an expert dental clinic triage assistant in Bengaluru.
Analyze the following patient intake data and evaluate buying intent & revenue priority.

Patient Data:
- Name: {cleaned_patient['name']}
- Procedure Code: {cleaned_patient['procedure_code']}
- Notes: {cleaned_patient['notes']}

High-Ticket Procedures List: {', '.join(HIGH_TICKET_PROCEDURES)}

Return ONLY a raw JSON object with the following fields:
{{
  "intent_score": <integer between 1 and 100>,
  "is_high_ticket": <boolean true/false>,
  "matched_procedures": [<list of matched high ticket procedures>],
  "reasoning": "<1-2 sentence explanation of the score>"
}}
"""
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            
            # Extract JSON from response
            response_text = response.text.strip()
            # Clean possible markdown codeblock wrappers
            if response_text.startswith("```"):
                response_text = re.sub(r"^```[a-z]*\n?", "", response_text)
                response_text = re.sub(r"\n?```$", "", response_text)

            ai_result = json.loads(response_text)
            ai_result["evaluator"] = "Gemini AI Engine"
            
            # Combine cleaned patient data with triage scoring
            return {
                "patient": cleaned_patient,
                "triage": ai_result
            }
        except Exception as e:
            # Fallback gracefully if API call fails (e.g. quota, network)
            triage_result = heuristic_lead_scorer(cleaned_patient)
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                triage_result["reasoning"] += " (Gemini API rate/quota limit hit — using fallback engine)"
            else:
                triage_result["reasoning"] += f" (Gemini API fallback: {err_msg.splitlines()[0]})"
            return {
                "patient": cleaned_patient,
                "triage": triage_result
            }
    else:
        # Step 3: Run Heuristic Scorer if GEMINI_API_KEY is not set
        triage_result = heuristic_lead_scorer(cleaned_patient)
        return {
            "patient": cleaned_patient,
            "triage": triage_result
        }


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
        }
    ]

    for idx, raw_lead in enumerate(test_leads, 1):
        print(f"--- TEST CASE {idx} ---")
        result = score_lead_intent(raw_lead)
        print(json.dumps(result, indent=2))
        print("\n")
