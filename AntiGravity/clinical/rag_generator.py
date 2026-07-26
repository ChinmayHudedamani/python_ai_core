import json
import os
import re
import difflib
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.security_shield import inspect_security_threats, is_gibberish_text

KB_PATH = Path(__file__).parent / "clinic_knowledge_base.json"


def load_knowledge_base() -> Dict[str, Any]:
    if KB_PATH.exists():
        with open(KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


CLINIC_KB = load_knowledge_base()


def fuzzy_token_match(query_word: str, target_text: str, cutoff: float = 0.82) -> bool:
    q_clean = query_word.lower().strip()
    t_clean = target_text.lower().strip()
    if q_clean in t_clean:
        return True
    tokens = t_clean.split()
    for token in tokens:
        ratio = difflib.SequenceMatcher(None, q_clean, token).ratio()
        if ratio >= cutoff:
            return True
    return False


def lookup_clinic_knowledge(query: str, procedure_code: str = "") -> Dict[str, Any]:
    query_lower = query.lower()
    proc_code_upper = procedure_code.upper().strip()

    matched_procedures = []
    matched_faqs = []
    matched_doctors = []

    # 1. Match Procedures
    for proc in CLINIC_KB.get("procedures", []):
        code_match = proc["code"] == proc_code_upper
        alias_match = any(fuzzy_token_match(alias, query_lower) for alias in proc.get("aliases", []))
        name_match = fuzzy_token_match(proc["name"], query_lower)
        if (code_match or alias_match or name_match) and proc not in matched_procedures:
            matched_procedures.append(proc)

    # 2. Match FAQs
    for faq in CLINIC_KB.get("faqs", []):
        if any(fuzzy_token_match(kw, query_lower) for kw in faq.get("keywords", [])) and faq not in matched_faqs:
            matched_faqs.append(faq)

    # 3. Match Doctors
    doctors_list = CLINIC_KB.get("doctors", [])
    for proc in matched_procedures:
        p_name = proc.get("name", "").lower()
        target_spec = "orthodontist" if ("invisalign" in p_name or "braces" in p_name or "aligner" in p_name) else "implantologist"
        for doc in doctors_list:
            if target_spec in doc.get("specialty", "").lower() and doc not in matched_doctors:
                matched_doctors.append(doc)

    if not matched_doctors and doctors_list:
        matched_doctors.append(doctors_list[0])

    has_grounded_facts = len(matched_procedures) > 0 or len(matched_faqs) > 0

    return {
        "matched_procedures": matched_procedures,
        "matched_faqs": matched_faqs,
        "matched_doctors": matched_doctors,
        "has_grounded_facts": has_grounded_facts
    }


def generate_zero_hallucination_response(raw_patient_data: Dict[str, Any]) -> Dict[str, Any]:
    raw_notes = raw_patient_data.get("notes", "")

    # Security Check
    security_audit = inspect_security_threats(raw_notes)

    if "PRESCRIPTION_MEDICATION_ATTEMPT" in security_audit["threat_categories"]:
        return {
            "whatsapp_response": (
                "Medical Disclaimer Notice:\n\n"
                "I am an automated clinical assistant and cannot prescribe medications or dosage advice legally.\n"
                "For your clinical safety, prescription of medication requires an in-person or telehealth evaluation by a licensed dentist.\n\n"
                "Our senior clinical team has been alerted and will contact you directly.\n"
                "Emergency Desk: +91-9988776655"
            )
        }

    if is_gibberish_text(raw_notes):
        return {
            "whatsapp_response": "Thank you for contacting Apex Dental Center. Please let us know how we can assist you with your dental health today!"
        }

    kb_facts = lookup_clinic_knowledge(raw_notes)

    # Build Clinical Response
    if kb_facts["matched_procedures"]:
        proc = kb_facts["matched_procedures"][0]
        doc = kb_facts["matched_doctors"][0] if kb_facts["matched_doctors"] else CLINIC_KB["doctors"][0]
        response_text = (
            f"Hello! Thank you for contacting Apex Dental Center, Koramangala.\n\n"
            f"📍 Treatment: {proc['name']}\n"
            f"💰 Price Range: {proc['price_range_inr']}\n"
            f"💳 EMI Options: {proc['emi_starting']}\n"
            f"👨‍⚕️ Specialist: {doc['name']} ({doc['title']})\n\n"
            f"Description: {proc['description']}\n\n"
            f"Would you like to schedule a consultation with {doc['name']} this week? "
            f"Reply '1' or 'YES' to reserve your slot."
        )
    elif kb_facts["matched_faqs"]:
        faq = kb_facts["matched_faqs"][0]
        response_text = (
            f"Hello! Thank you for contacting Apex Dental Center.\n\n"
            f"Q: {faq['question']}\n"
            f"A: {faq['answer']}\n\n"
            f"Would you like to speak to our clinic receptionist or book a consultation? Reply '1' to confirm."
        )
    else:
        response_text = (
            "Hello! Thank you for contacting Apex Dental Center & Implant Institute, Koramangala.\n\n"
            "We offer complete dental care including Invisalign clear aligners, dental implants, root canal treatments, and smile makeovers.\n"
            "Chief Dentist: Dr. Chinmay Hudedamani.\n\n"
            "How can we assist you today?"
        )

    return {
        "whatsapp_response": response_text,
        "grounding_facts": kb_facts
    }
