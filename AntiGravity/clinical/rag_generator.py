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
                "For your safety, I am unable to prescribe medications or provide dosage advice over chat. "
                "Dental prescriptions require a quick clinical evaluation by a licensed dentist to prevent adverse reactions.\n\n"
                "I've flagged your request for our clinical team, and our receptionist will call you directly. "
                "If you are in severe pain or need immediate help, please call our emergency desk at +91-9988776655."
            )
        }

    if is_gibberish_text(raw_notes):
        return {
            "whatsapp_response": "Hello! Thanks for reaching out to Apex Dental Center in Koramangala. 😊 How can I help you with your teeth or appointments today?"
        }

    kb_facts = lookup_clinic_knowledge(raw_notes)

    # Build Natural Human Receptionist Response
    if kb_facts["matched_procedures"]:
        proc = kb_facts["matched_procedures"][0]
        doc = kb_facts["matched_doctors"][0] if kb_facts["matched_doctors"] else CLINIC_KB["doctors"][0]
        response_text = (
            f"Hello! Thanks for reaching out to Apex Dental Center in Koramangala. 😊\n\n"
            f"Regarding {proc['name']}, our complete packages range between {proc['price_range_inr']}. "
            f"We also offer easy 0% interest EMI options starting at {proc['emi_starting']} so treatment is comfortable for your budget.\n\n"
            f"{proc['description']}\n\n"
            f"Our specialist, {doc['name']} ({doc['title']}), handles all our {proc['name']} consultations. "
            f"Would you like me to check available slots for you to see {doc['name']} this week?"
        )
    elif kb_facts["matched_faqs"]:
        faq = kb_facts["matched_faqs"][0]
        response_text = (
            f"Hello! Thanks for asking about that. 😊\n\n"
            f"{faq['answer']}\n\n"
            f"Please let me know if you would like to book a consultation at our Koramangala clinic or if you have any other questions I can help answer!"
        )
    else:
        response_text = (
            "Hello! Welcome to Apex Dental Center in Koramangala. 😊\n\n"
            "I'm here to help you with treatment information, pricing, or booking your dental visit. "
            "We offer Invisalign clear aligners, dental implants, root canal treatments, and smile makeovers under our Chief Dentist, Dr. Chinmay Hudedamani.\n\n"
            "What can I help answer for you today?"
        )

    return {
        "whatsapp_response": response_text,
        "grounding_facts": kb_facts
    }
