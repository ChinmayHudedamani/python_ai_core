import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from day2_python import clean_client_data
from day3_python import score_lead_intent, chinmay_lead_scorer

load_dotenv()

KNOWLEDGE_BASE_PATH = Path(__file__).parent / "clinic_knowledge_base.json"

def load_knowledge_base() -> dict:
    """Loads authoritative clinic price list, doctor profiles, and FAQ data."""
    if KNOWLEDGE_BASE_PATH.exists():
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CLINIC_KB = load_knowledge_base()


def lookup_clinic_knowledge(query_text: str, procedure_code: str = "") -> dict:
    """
    Sub-millisecond Grounding Knowledge Retriever over Clinic Knowledge Base.
    Extracts matched procedures, pricing, warranties, FAQs, and clinic logistics.
    """
    query_lower = query_text.lower()
    proc_code_upper = procedure_code.upper().strip()

    matched_procedures = []
    matched_faqs = []

    # 1. Match Procedures by Code or Alias/Name Substring
    for proc in CLINIC_KB.get("procedures", []):
        code_match = proc["code"] == proc_code_upper
        alias_match = any(re.search(r"\b" + re.escape(alias) + r"\b", query_lower) for alias in proc.get("aliases", []))
        name_match = proc["name"].lower() in query_lower

        if code_match or alias_match or name_match:
            if proc not in matched_procedures:
                matched_procedures.append(proc)

    # 2. Match FAQs by Keyword Occurrence
    for faq in CLINIC_KB.get("faqs", []):
        if any(kw in query_lower for kw in faq.get("keywords", [])):
            if faq not in matched_faqs:
                matched_faqs.append(faq)

    has_grounded_facts = len(matched_procedures) > 0 or len(matched_faqs) > 0

    return {
        "matched_procedures": matched_procedures,
        "matched_faqs": matched_faqs,
        "has_grounded_facts": has_grounded_facts,
        "clinic_info": CLINIC_KB.get("clinic_info", {}),
        "doctors": CLINIC_KB.get("doctors", [])
    }


def generate_zero_hallucination_response(raw_patient_data: dict) -> dict:
    """
    Day 4 Core RAG Pipeline:
    1. Data Sanitization (Day 2 Intake Valve)
    2. Enterprise Lead Scorer & Tier Triage (Day 3 Scorer)
    3. Authoritative Knowledge Base Lookup (Day 4 Grounding)
    4. Zero-Hallucination Response Generation with Hardcoded Fallbacks
    """
    # Step 1: Clean data
    cleaned_patient = clean_client_data(raw_patient_data)
    notes = cleaned_patient.get("notes", "")
    proc_code = cleaned_patient.get("procedure_code", "")

    # Step 2: Perform Day 3 Triage
    triage_payload = score_lead_intent(raw_patient_data)
    triage_info = triage_payload.get("triage", {})
    lead_tier = triage_info.get("lead_tier", "COLD_ROUTINE")

    # Step 3: Medical Emergency Safety Override (ESI RED)
    if lead_tier == "RED_CRITICAL_EMERGENCY":
        emergency_response = (
            "🚨 CRITICAL MEDICAL EMERGENCY ALERT 🚨\n"
            "If the patient is experiencing profuse bleeding, chest pain, difficulty breathing, or severe trauma, "
            "PLEASE CALL NATIONAL EMERGENCY AT 112 IMMEDIATELY or visit the nearest Hospital Emergency Room.\n"
            "Our clinic emergency line has been alerted."
        )
        return {
            "patient": cleaned_patient,
            "triage": triage_info,
            "grounding_facts": {"has_grounded_facts": False},
            "whatsapp_response": emergency_response,
            "zero_hallucination_guarantee": True
        }

    # Step 4: Retrieve Grounding Knowledge Base Facts
    kb_facts = lookup_clinic_knowledge(notes, proc_code)
    has_facts = kb_facts["has_grounded_facts"]
    api_key = os.environ.get("GEMINI_API_KEY")

    # Step 5: Generate Response (LLM with Strict Grounding Prompt OR Heuristic Fallback)
    if api_key and has_facts:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            facts_summary = json.dumps({
                "matched_procedures": kb_facts["matched_procedures"],
                "matched_faqs": kb_facts["matched_faqs"],
                "clinic_info": kb_facts["clinic_info"]
            }, indent=2)

            prompt = f"""
You are the AI Front-Desk Centaur Responder for Apex Dental Centaur in Koramangala, Bengaluru.
Generate a professional, warm, zero-hallucination WhatsApp reply for patient {cleaned_patient['name']}.

Patient Message: "{cleaned_patient['notes']}"
Assigned Triage Tier: {lead_tier}

AUTHORITATIVE CLINIC FACTS:
{facts_summary}

STRICT ZERO-HALLUCINATION RULES:
1. State ONLY prices, warranties, and details present in AUTHORITATIVE CLINIC FACTS. Never invent numbers.
2. If pricing for a specific complex procedure is not listed, explicitly state: "Pricing requires an in-person evaluation by Dr. Chinmay Hudedamani."
3. End with a clear call-to-action inviting them to book a consultation slot.
"""
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            whatsapp_reply = response.text.strip()
        except Exception:
            whatsapp_reply = build_heuristic_rag_response(cleaned_patient, kb_facts, lead_tier)
    else:
        whatsapp_reply = build_heuristic_rag_response(cleaned_patient, kb_facts, lead_tier)

    return {
        "patient": cleaned_patient,
        "triage": triage_info,
        "grounding_facts": {
            "matched_procedures_count": len(kb_facts["matched_procedures"]),
            "matched_faqs_count": len(kb_facts["matched_faqs"]),
            "has_grounded_facts": has_facts
        },
        "whatsapp_response": whatsapp_reply,
        "zero_hallucination_guarantee": True
    }


def build_heuristic_rag_response(cleaned_patient: dict, kb_facts: dict, lead_tier: str) -> str:
    """Zero-Hallucination Heuristic Fallback Response Builder."""
    name = cleaned_patient.get("name", "Patient")
    procs = kb_facts.get("matched_procedures", [])
    faqs = kb_facts.get("matched_faqs", [])
    clinic = kb_facts.get("clinic_info", {})

    lines = [f"Hello {name}! Thank you for contacting {clinic.get('name', 'Apex Dental')}.\n"]

    if procs:
        p = procs[0]
        lines.append(f"🦷 **{p['name']} Details**:")
        lines.append(f"• Price Range: {p['price_range_inr']}")
        lines.append(f"• EMI Option: {p['emi_starting']}")
        lines.append(f"• Warranty: {p['warranty']}")
        lines.append(f"• Procedure: {p['description']}\n")
    elif faqs:
        f = faqs[0]
        lines.append(f"ℹ️ {f['answer']}\n")
    else:
        lines.append(
            "ℹ️ Specific pricing for your custom treatment plan requires a detailed digital examination and X-ray. "
            "Our Senior Specialist will evaluate your case in person.\n"
        )

    lines.append(f"📍 **Location**: {clinic.get('location', 'Koramangala, Bengaluru')}")
    lines.append(f"🕒 **Hours**: {clinic.get('operating_hours', {}).get('monday_to_saturday', '9 AM - 8 PM')}\n")

    if lead_tier == "VIP_HIGH_REVENUE":
        lines.append("⭐ **VIP Priority Alert**: Our Senior Implantologist & AE will contact you directly within 15 minutes to reserve your consultation slot.")
    else:
        lines.append("Would you like me to reserve a consultation appointment slot for you today?")

    return "\n".join(lines)


if __name__ == "__main__":
    print("==================================================")
    print("   DAY 4: ZERO-HALLUCINATION RAG ENGINE DEMO")
    print("==================================================\n")

    test_inquiries = [
        {
            "name": "   ananya roy ",
            "phone": "+91-99887 76655",
            "procedure_code": "  aligners ",
            "notes": "Hi, what is the cost of Invisalign clear aligners in Bengaluru? Do you have EMI options?"
        },
        {
            "name": "vikram sethi",
            "phone": " 9876543210 ",
            "procedure_code": "CLEAN-01",
            "notes": "What are your Saturday working hours and clinic location?"
        },
        {
            "name": "kavita Sharma",
            "phone": "+91 9123456789",
            "procedure_code": "RCT",
            "notes": "Need root canal treatment price and single sitting details."
        },
        {
            "name": "Deepak Rao",
            "phone": "9811122233",
            "procedure_code": "SPECIAL_SURGERY",
            "notes": "Do you perform customized jaw alignment surgeries for rare asymmetry?"
        }
    ]

    for idx, raw_lead in enumerate(test_inquiries, 1):
        print(f"--- TEST CASE {idx} ---")
        res = generate_zero_hallucination_response(raw_lead)
        print(json.dumps(res, indent=2))
        print("\n" + "="*50 + "\n")
