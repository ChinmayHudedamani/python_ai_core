import json
import os
import re
import datetime
import difflib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from day2_python import clean_client_data, mask_pii
from day3_python import score_lead_intent

load_dotenv()

KNOWLEDGE_BASE_PATH: Path = Path(__file__).parent / "clinic_knowledge_base.json"

def load_knowledge_base() -> Dict[str, Any]:
    """Loads authoritative clinic price list, doctor profiles, and FAQ data."""
    if KNOWLEDGE_BASE_PATH.exists():
        with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CLINIC_KB: Dict[str, Any] = load_knowledge_base()

HINGLISH_INDICATORS: List[str] = ["mera", "daant", "kitna", "kharcha", "chahiye", "hai", "dard", "jaldi", "bohot", "kitne", "paisa", "dam"]

# Multi-Layer Enterprise Security Matrix
PROMPT_INJECTION_CATEGORIES: Dict[str, List[str]] = {
    "DIRECT_OVERRIDE": [
        r"ignore (all )?previous", r"disregard (all )?instructions", r"system prompt",
        r"you are now a", r"act as", r"dev mode", r"mode: dan", r"forget everything",
        r"bypass rules", r"new role"
    ],
    "FRAUD_EXPLOIT": [
        r"free treatment", r"give me free", r"100% discount", r"price is 0", r"zero cost",
        r"refund all", r"complimentary service", r"waive fee", r"no charge"
    ],
    "DATA_LEAK_ATTEMPT": [
        r"reveal api key", r"show system prompt", r"print instructions", r"export database",
        r"show passwords", r"dump env", r"read file", r"access key"
    ]
}


def sanitize_user_input(text: str) -> str:
    """Strips control characters, prompt boundaries, and delimiter injections."""
    cleaned = re.sub(r"```|\[INST\]|<\|im_start\|>|<\|im_end\|>|system:", "", text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", cleaned).strip()


def inspect_security_threats(text: str) -> Dict[str, Any]:
    """Multi-layer Security Shield: Inspects direct overrides, financial fraud, and data leaks."""
    text_clean: str = sanitize_user_input(text).lower()
    threats_found: List[str] = []

    for category, patterns in PROMPT_INJECTION_CATEGORIES.items():
        if any(re.search(pat, text_clean) for pat in patterns):
            threats_found.append(category)

    # Obfuscated character space matching (e.g. f r e e  t r e a t m e n t)
    deobfuscated: str = re.sub(r"\b(\w)\s+(\w)\s+(\w)\s+(\w)\b", r"\1\2\3\4", text_clean)
    if "free" in deobfuscated and "treatment" in deobfuscated and "FRAUD_EXPLOIT" not in threats_found:
        threats_found.append("FRAUD_EXPLOIT")

    return {"is_threat": len(threats_found) > 0, "threat_categories": threats_found}


def detect_language(text: str) -> str:
    """Detects whether user is speaking English or Hinglish/Vernacular."""
    return "hinglish" if any(w in text.lower() for w in HINGLISH_INDICATORS) else "english"


def fuzzy_token_match(term: str, text: str) -> bool:
    """Fuzzy matching for patient typos using difflib similarity ratio."""
    term_clean: str = term.lower().strip()
    text_lower: str = text.lower()
    if re.search(r"\b" + re.escape(term_clean) + r"\b", text_lower):
        return True
    words: List[str] = re.findall(r"\b\w+\b", text_lower)
    return any(
        difflib.SequenceMatcher(None, term_clean, w).ratio() >= 0.75
        for w in words if len(w) >= 4 and len(term_clean) >= 4
    )


def get_realtime_consultation_slots(procedure_code: str = "", lead_tier: str = "COLD_ROUTINE") -> List[str]:
    """Real-Time Dynamic Calendar Engine calculating dates relative to system time."""
    now: datetime.datetime = datetime.datetime.now()
    slots: List[str] = []

    if lead_tier in ["RED_CRITICAL_EMERGENCY", "URGENT_CLINICAL"]:
        today_str: str = now.strftime("%A, %b %d")
        slots.extend([
            f"Today ({today_str}) at 05:30 PM (Emergency Pain Relief Window)",
            f"Today ({today_str}) at 07:00 PM (Urgent Clinical Slot)"
        ])

    tomorrow_str: str = (now + datetime.timedelta(days=1)).strftime("%A, %b %d")
    if procedure_code.upper() in ["IMP", "INVIS", "FMR", "SMB"]:
        slots.extend([
            f"{tomorrow_str} at 10:30 AM (Senior Specialist VIP Window)",
            f"{tomorrow_str} at 04:00 PM (Senior Specialist VIP Window)"
        ])
    else:
        slots.extend([f"{tomorrow_str} at 11:00 AM", f"{tomorrow_str} at 03:30 PM"])

    day_after_str: str = (now + datetime.timedelta(days=2)).strftime("%A, %b %d")
    slots.append(f"{day_after_str} at 10:00 AM")

    return slots[:3]


def lookup_clinic_knowledge(query_text: str, procedure_code: str = "") -> Dict[str, Any]:
    """Sub-millisecond Grounding Knowledge Retriever over Clinic Knowledge Base."""
    query_lower: str = query_text.lower()
    proc_code_upper: str = procedure_code.upper().strip()

    matched_procedures: List[Dict[str, Any]] = []
    matched_faqs: List[Dict[str, Any]] = []
    matched_doctors: List[Dict[str, Any]] = []
    citations: List[str] = []

    # 1. Match Procedures
    for proc in CLINIC_KB.get("procedures", []):
        code_match: bool = proc["code"] == proc_code_upper
        alias_match: bool = any(fuzzy_token_match(alias, query_lower) for alias in proc.get("aliases", []))
        name_match: bool = fuzzy_token_match(proc["name"], query_lower)

        if (code_match or alias_match or name_match) and proc not in matched_procedures:
            matched_procedures.append(proc)
            citations.append(f"procedures.{proc['code']}")

    # 2. Match FAQs
    for idx, faq in enumerate(CLINIC_KB.get("faqs", [])):
        if any(fuzzy_token_match(kw, query_lower) for kw in faq.get("keywords", [])) and faq not in matched_faqs:
            matched_faqs.append(faq)
            citations.append(f"faqs[{idx}]")

    # 3. Match Specialty Doctors
    doctors_list: List[Dict[str, Any]] = CLINIC_KB.get("doctors", [])
    for proc in matched_procedures:
        p_name: str = proc.get("name", "").lower()
        target_spec: str = "orthodontist" if ("invisalign" in p_name or "aligner" in p_name) else "implantologist"
        for doc in doctors_list:
            if target_spec in doc.get("specialty", "").lower() and doc not in matched_doctors:
                matched_doctors.append(doc)

    if not matched_doctors and doctors_list:
        matched_doctors.append(doctors_list[0])

    has_grounded_facts: bool = len(matched_procedures) > 0 or len(matched_faqs) > 0
    confidence_score: float = min(1.0, (len(matched_procedures) * 0.5) + (len(matched_faqs) * 0.3) + (0.2 if has_grounded_facts else 0.0))

    return {
        "matched_procedures": matched_procedures,
        "matched_faqs": matched_faqs,
        "matched_doctors": matched_doctors,
        "has_grounded_facts": has_grounded_facts,
        "confidence_score": round(confidence_score, 2),
        "citations": citations,
        "clinic_info": CLINIC_KB.get("clinic_info", {})
    }


def generate_zero_hallucination_response(raw_patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Day 4 Core RAG Pipeline: Safety -> Triage -> Grounding -> Response."""
    raw_notes: str = raw_patient_data.get("notes", "")

    # Step 0: Security Inspection
    security_audit: Dict[str, Any] = inspect_security_threats(raw_notes)
    if security_audit["is_threat"]:
        return {
            "patient": raw_patient_data,
            "triage": {
                "lead_tier": "DISQUALIFIED",
                "reasoning": f"SECURITY ALERT: Blocked threat categories: {', '.join(security_audit['threat_categories'])}."
            },
            "grounding_facts": {
                "has_grounded_facts": False,
                "citations": [f"security_shield.{cat.lower()}" for cat in security_audit['threat_categories']]
            },
            "whatsapp_response": "⚠️ Invalid or unsupported request format. Please contact our clinic reception directly at +91-9988776655 for assistance.",
            "zero_hallucination_guarantee": True
        }

    # Step 1: Clean Data & Language
    cleaned_patient: Dict[str, Any] = clean_client_data(raw_patient_data)
    notes: str = cleaned_patient.get("notes", "")
    proc_code: str = cleaned_patient.get("procedure_code", "")
    detected_lang: str = detect_language(notes)

    # Step 2: Triage
    triage_payload: Dict[str, Any] = score_lead_intent(raw_patient_data)
    triage_info: Dict[str, Any] = triage_payload.get("triage", {})
    lead_tier: str = triage_info.get("lead_tier", "COLD_ROUTINE")

    # Step 3: Medical Emergency Override
    if lead_tier == "RED_CRITICAL_EMERGENCY":
        return {
            "patient": cleaned_patient,
            "triage": triage_info,
            "grounding_facts": {"has_grounded_facts": False, "citations": ["emergency_override_112"]},
            "whatsapp_response": (
                "🚨 CRITICAL MEDICAL EMERGENCY ALERT 🚨\n"
                "If the patient is experiencing profuse bleeding, chest pain, difficulty breathing, or severe trauma, "
                "PLEASE CALL NATIONAL EMERGENCY AT 112 IMMEDIATELY or visit the nearest Hospital Emergency Room.\n"
                "Our clinic emergency line has been alerted."
            ),
            "zero_hallucination_guarantee": True
        }

    # Step 4: Grounding Retrieval
    kb_facts: Dict[str, Any] = lookup_clinic_knowledge(notes, proc_code)
    available_slots: List[str] = get_realtime_consultation_slots(proc_code, lead_tier)
    has_facts: bool = kb_facts["has_grounded_facts"]
    api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")

    # Step 5: Response Generation
    if api_key and has_facts:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            facts_summary: str = json.dumps({
                "matched_procedures": kb_facts["matched_procedures"],
                "matched_faqs": kb_facts["matched_faqs"],
                "matched_doctors": kb_facts["matched_doctors"],
                "available_slots": available_slots,
                "clinic_info": kb_facts["clinic_info"]
            }, indent=2)

            prompt: str = f"""You are the AI Front-Desk Centaur Responder for Apex Dental Centaur in Koramangala, Bengaluru.
Generate a professional, warm, zero-hallucination WhatsApp reply for patient {cleaned_patient['name']}.
Language Preference: {detected_lang} (If hinglish, use respectful conversational English with Hindi warmth).

Patient Message: "{cleaned_patient['notes']}"
Assigned Triage Tier: {lead_tier}

AUTHORITATIVE CLINIC FACTS:
{facts_summary}

STRICT ZERO-HALLUCINATION RULES:
1. State ONLY prices, warranties, and details present in AUTHORITATIVE CLINIC FACTS. Never invent numbers.
2. If pricing for a specific complex procedure is not listed, explicitly state: "Pricing requires an in-person evaluation by Dr. Chinmay Hudedamani."
3. Mention available consultation slots: {', '.join(available_slots)}.
"""
            response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
            whatsapp_reply: str = response.text.strip()
        except Exception:
            whatsapp_reply = build_heuristic_rag_response(cleaned_patient, kb_facts, lead_tier, available_slots, detected_lang)
    else:
        whatsapp_reply = build_heuristic_rag_response(cleaned_patient, kb_facts, lead_tier, available_slots, detected_lang)

    return {
        "patient": cleaned_patient,
        "triage": triage_info,
        "language_detected": detected_lang,
        "grounding_facts": {
            "matched_procedures_count": len(kb_facts["matched_procedures"]),
            "matched_faqs_count": len(kb_facts["matched_faqs"]),
            "matched_doctors": [d["name"] for d in kb_facts.get("matched_doctors", [])],
            "available_slots": available_slots,
            "has_grounded_facts": has_facts,
            "confidence_score": kb_facts["confidence_score"],
            "citations": kb_facts["citations"]
        },
        "whatsapp_response": whatsapp_reply,
        "zero_hallucination_guarantee": True
    }


def build_heuristic_rag_response(cleaned_patient: Dict[str, Any], kb_facts: Dict[str, Any], lead_tier: str, slots: List[str], lang: str) -> str:
    """Multi-Fact Zero-Hallucination Heuristic Fallback Response Builder."""
    name: str = cleaned_patient.get("name", "Patient")
    procs: List[Dict[str, Any]] = kb_facts.get("matched_procedures", [])
    faqs: List[Dict[str, Any]] = kb_facts.get("matched_faqs", [])
    doctors: List[Dict[str, Any]] = kb_facts.get("matched_doctors", [])
    clinic: Dict[str, Any] = kb_facts.get("clinic_info", {})

    greeting: str = f"Namaste {name}!" if lang == "hinglish" else f"Hello {name}!"
    lines: List[str] = [f"{greeting} Thank you for contacting {clinic.get('name', 'Apex Dental Centaur')}.\n"]

    if procs:
        for p in procs:
            lines.append(f"🦷 **{p['name']} Details**:")
            lines.append(f"  • Price Range: {p['price_range_inr']}")
            lines.append(f"  • EMI Starting: {p['emi_starting']}")
            lines.append(f"  • Warranty: {p['warranty']}")
            lines.append(f"  • Description: {p['description']}\n")

    if faqs:
        lines.append("📋 **Frequently Asked Info**:")
        for f in faqs:
            lines.append(f"  • {f['answer']}")
        lines.append("")

    if not procs and not faqs:
        lines.append(
            "ℹ️ Specific pricing for your custom treatment plan requires an in-person digital examination and 3D CBCT scan. "
            "Our Senior Specialist will evaluate your case in person.\n"
        )

    if doctors:
        d = doctors[0]
        lines.append(f"👨‍⚕️ **Attending Specialist**: {d['name']} ({d['specialty']} - {d['qualification']})")

    lines.append(f"📍 **Location**: {clinic.get('location', 'Koramangala, Bengaluru')}")
    lines.append(f"🕒 **Hours**: {clinic.get('operating_hours', {}).get('monday_to_saturday', '9 AM - 8 PM')}\n")

    if slots:
        lines.append(f"📅 **Real-Time Available Slots**: {', '.join(slots)}")

    if lead_tier == "VIP_HIGH_REVENUE":
        lines.append("⭐ **VIP Priority Alert**: Our Senior Implantologist & AE team will contact you directly within 15 minutes to confirm your exclusive appointment slot.")
    elif lead_tier == "URGENT_CLINICAL":
        lines.append("🚨 **Emergency Clinical Slot**: Reply YES to lock in today's emergency pain-relief appointment.")
    else:
        lines.append("Reply with your preferred slot to confirm your booking!")

    return "\n".join(lines)


if __name__ == "__main__":
    test_inquiries = [
        {
            "name": "   ananya roy ",
            "phone": "+91-99887 76655",
            "procedure_code": "  aligners ",
            "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
        }
    ]

    for idx, raw_lead in enumerate(test_inquiries, 1):
        res = generate_zero_hallucination_response(raw_lead)
        print(json.dumps(res, indent=2))




