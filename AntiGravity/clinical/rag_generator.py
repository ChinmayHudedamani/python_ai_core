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
    query_clean = raw_notes.strip().lower()

    # 0. Direct Simple Greetings
    if query_clean in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "namaste", "hi there", "hello there"]:
        return {
            "whatsapp_response": "Thank you for contacting Apex Dental Center. How may I help you today?"
        }

    # Security Check
    security_audit = inspect_security_threats(raw_notes)

    if "PRESCRIPTION_MEDICATION_ATTEMPT" in security_audit["threat_categories"]:
        return {
            "whatsapp_response": (
                "For your safety, I am unable to prescribe medications or provide dosage advice over chat. "
                "Dental prescriptions require a quick evaluation by a licensed dentist.\n\n"
                "I have notified our clinical desk, and our team will call you directly. "
                "For urgent pain or emergency assistance, please call us at +91-9988776655."
            )
        }

    if is_gibberish_text(raw_notes):
        return {
            "whatsapp_response": "Thank you for contacting Apex Dental Center. How may I help you today?"
        }

    kb_facts = lookup_clinic_knowledge(raw_notes)

    # Build Focused, Step-by-Step Receptionist Response (No Info Dumping)
    if kb_facts["matched_procedures"]:
        proc = kb_facts["matched_procedures"][0]
        doc = kb_facts["matched_doctors"][0] if kb_facts["matched_doctors"] else CLINIC_KB["doctors"][0]

        is_price_query = any(w in query_clean for w in ["cost", "price", "rate", "fee", "kharcha", "emi", "discount", "package", "how much"])
        is_doctor_query = any(w in query_clean for w in ["doctor", "dentist", "specialist", "who", "qualification", "experience"])

        if is_price_query:
            response_text = (
                f"Our {proc['name']} packages range between {proc['price_range_inr']}. "
                f"We also offer 0% interest EMI options starting at {proc['emi_starting']}.\n\n"
                f"Would you like to schedule a consultation with {doc['name']} or know more about what the package includes?"
            )
        elif is_doctor_query:
            response_text = (
                f"Our {proc['name']} consultations are led by {doc['name']} ({doc['title']}), "
                f"who has {doc['experience_years']} years of specialized experience.\n\n"
                f"Would you like me to check available consultation slots for you this week?"
            )
        else:
            response_text = (
                f"Regarding {proc['name']}, packages range between {proc['price_range_inr']} with 0% EMI options from {proc['emi_starting']}.\n\n"
                f"Would you like to book a consultation slot with {doc['name']} or ask a specific question?"
            )

    elif kb_facts["matched_faqs"]:
        faq = kb_facts["matched_faqs"][0]
        response_text = (
            f"{faq['answer']}\n\n"
            f"Please let me know if you would like to visit our Koramangala clinic or if you have any other questions!"
        )
    else:
        response_text = (
            "Thank you for reaching out to Apex Dental Center in Koramangala. "
            "We offer clear aligners, dental implants, single-visit root canals, and smile makeovers.\n\n"
            "How may I help you today?"
        )

    return {
        "whatsapp_response": response_text,
        "grounding_facts": kb_facts
    }
