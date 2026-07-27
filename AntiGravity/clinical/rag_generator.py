# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI - Proprietary Clinical AI Assistant & Automated RAG Engine created by Chinmay Hudedamani.

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


def sanitize_llm_response(response_text: str) -> str:
    """Post-processing sanitizer against medical liability jailbreaks and fake discount injection."""
    forbidden_terms = [
        r"\bamoxicillin\b", r"\bibuprofen\b", r"\bpenicillin\b", r"\bvicodin\b", r"\btramadol\b",
        r"\bdiscount100\b", r"\b100%\s*off\b", r"\bfree\s*appointment\b", r"\bbypass\s*payment\b"
    ]
    clean_text = response_text
    for pattern in forbidden_terms:
        if re.search(pattern, clean_text, flags=re.IGNORECASE):
            clean_text = re.sub(pattern, "[REDACTED_CLINICAL_POLICY]", clean_text, flags=re.IGNORECASE)
    return clean_text


def check_operating_hours_validity(query_clean: str) -> tuple:
    """Checks if requested time is outside clinic operating hours (9:00 AM - 8:00 PM Mon-Sat / 10:00 AM - 2:00 PM Sun)."""
    # Match patterns like: 10:30pm, 10 30pm, 10pm, 9:30pm, 11pm, 8:30pm, 9pm, 10:30 pm, 4am, etc.
    time_match = re.search(r"\b(1[0-2]|[1-9])(?::([0-5]\d)|\s+([0-5]\d))?\s*(am|pm)?\b", query_clean)
    if time_match and (time_match.group(2) or time_match.group(3) or time_match.group(4) or "am" in query_clean or "pm" in query_clean):
        hour = int(time_match.group(1))
        mins = int(time_match.group(2) or time_match.group(3) or 0)
        raw_ampm = (time_match.group(4) or "").lower()
        if not raw_ampm:
            raw_ampm = "pm" if "pm" in query_clean else "am"
        ampm = raw_ampm

        if ampm == "pm" and hour < 12:
            hour24 = hour + 12
        elif ampm == "am" and hour == 12:
            hour24 = 0
        else:
            hour24 = hour

        is_sunday = "sun" in query_clean or "sunday" in query_clean

        if is_sunday:
            if hour24 < 10 or (hour24 == 14 and mins > 0) or hour24 > 14:
                time_str = f"{hour}:{mins:02d} {ampm.upper()}" if mins else f"{hour} {ampm.upper()}"
                return False, time_str
        else:
            if hour24 < 9 or (hour24 == 20 and mins > 0) or hour24 > 20:
                time_str = f"{hour}:{mins:02d} {ampm.upper()}" if mins else f"{hour} {ampm.upper()}"
                return False, time_str

    return True, ""


def generate_zero_hallucination_response(raw_patient_data: Dict[str, Any]) -> Dict[str, Any]:
    raw_notes = raw_patient_data.get("notes", "")
    patient_name = raw_patient_data.get("name", "").strip()
    if patient_name == "Patient" or not patient_name:
        patient_name = ""
    else:
        patient_name = patient_name.title()

    name_greeting = f", {patient_name}" if patient_name else ""
    query_clean = raw_notes.strip().lower()

    # 0a. APEX AI Warm Greeting & Name Inquiry
    if query_clean in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "namaste", "hi there", "hello there", "hi mai", "hello mai", "hi apex", "hello apex", "hi apex ai"]:
        if patient_name:
            return {
                "whatsapp_response": f"Hey there{name_greeting}! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute. 🌿\n\nHow can I help you today? Are you looking to discuss a dental treatment (such as Invisalign clear aligners, laser root canal, or 3D implants), check pricing, or book a consultation?"
            }
        return {
            "whatsapp_response": "Hey there! 👋 I'm APEX AI, your clinical assistant from Apex Dental Center & Implant Institute, Koramangala. 🌿\n\nI'm here to guide you, answer your health questions, and connect you to care when needed.\n\nTo start, may I know your name?"
        }

    # 0b. Direct Gratitude & Goodbye Detection
    if any(w in query_clean for w in ["thank you", "thanks", "thank u", "thx", "thankyou", "thanks a lot", "thank you so much", "bye", "goodbye", "ok thanks", "okay thanks", "dhanyawad", "dhanyavad", "shukriya", "shukriyaa"]):
        return {
            "whatsapp_response": f"You're very welcome{name_greeting}! 😊 It was a pleasure assisting you. Have a wonderful day, and please feel free to reach out anytime if you need anything else from Apex Dental Center!"
        }

    # 0c. Health Concern Inquiry Handler
    if any(kw in query_clean for kw in ["health concern", "health concerns", "health issue", "health issues", "health problem", "symptom", "symptoms", "dental concern"]):
        return {
            "whatsapp_response": (
                f"What is your specific health concern or symptom{name_greeting} (such as toothache, bleeding gums, chipped tooth, or sensitivity)? 😊\n\n"
                f"Would you like me to book a consultation slot with a specialist doctor in this field, or request a quick callback from our clinic reception desk?"
            )
        }

    # 0d. Treatment Options List Handler
    if any(kw in query_clean for kw in ["treatment options", "treatments", "check treatment options", "available treatments", "list of treatments", "treatment list", "services", "procedures"]):
        return {
            "whatsapp_response": (
                f"Here is the list of modern dental treatments available at Apex Dental Center & Implant Institute{name_greeting}: 🦷\n\n"
                f"1. 💎 Invisalign Clear Aligners (Orthodontics & Teeth Straightening)\n"
                f"2. 🦷 3D Guided Dental Implants (Permanent Tooth Replacement)\n"
                f"3. ⚡ Single-Visit Laser Root Canal Treatment (Painless RCT)\n"
                f"4. ✨ Laser Teeth Whitening & Smile Makeovers\n"
                f"5. 🛡️ Tooth Fillings & Cosmetic Bonding\n"
                f"6. 🦷 Wisdom Tooth Extraction & Oral Surgery\n"
                f"7. 🪥 Ultrasonic Scaling & Deep Teeth Cleaning\n\n"
                f"Which treatment would you like more details or pricing on? Or would you like to check available consultation slots for tomorrow?"
            )
        }

    # 0e. Clinic Reception Callback Handler
    if any(kw in query_clean for kw in ["callback", "call me", "reception", "request callback", "call back", "receptionist"]):
        return {
            "whatsapp_response": (
                f"Understood{name_greeting}! I have registered a priority callback request with our reception team at Apex Dental Center. 📞\n\n"
                f"Our clinic receptionist will call your registered phone number shortly.\n\n"
                f"Would you also like me to reserve a consultation slot for you tomorrow with Dr. Chinmay Hudedamani?"
            )
        }

    # 0f. Comprehensive Acceptance / Affirmative Keywords Handler (Sure, Why Not, Yeah, Sounds Good, Go Ahead, etc.)
    acceptance_keywords = [
        "sure", "why not", "yeah", "yep", "yup", "definitely", "absolutely", "of course", "ok", "okay",
        "fine", "alright", "sounds good", "sounds great", "book it", "go ahead", "yes please", "please do",
        "cool", "perfect", "lock it", "confirm", "1", "yes", "proceed", "great", "awesome", "sure thing",
        "why not book it", "do it", "check slots", "lock my slot", "yes book", "book a slot", "book consultation",
        "schedule it", "slot please", "hold it", "reserve it", "reserve slot", "im in", "let's do it", "lets do it",
        "done", "set it up", "kardo", "kar do", "haan", "ha", "sahi hai", "sahi h", "chalega", "book kardo", "pay", "lock"
    ]
    is_affirmative = any(query_clean == kw or query_clean.startswith(kw) or f" {kw} " in f" {query_clean} " for kw in acceptance_keywords)

    if is_affirmative:
        return {
            "whatsapp_response": (
                f"Great choice{name_greeting}! I can hold that time for you. 😊\n\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Location: Apex Dental Center, Koramangala, Bengaluru\n\n"
                f"Available slots tomorrow:\n"
                f"• 10:30 AM\n"
                f"• 04:00 PM\n\n"
                f"To secure this slot, could you please provide your 10-digit registered mobile number?"
            )
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
            "whatsapp_response": f"How can I help you today{name_greeting}? Feel free to ask about our treatments or booking a consultation at Apex Dental Center!"
        }

    kb_facts = lookup_clinic_knowledge(raw_notes)

    # 0c. Appointment / Slot / Timing Query Detection
    is_slot_query = any(w in query_clean for w in [
        "appointment", "appointments", "slot", "slots", "schedule", "timing", "timings",
        "available", "visit", "open", "hours", "enquire", "inquire", "time", "book", "booking"
    ])

    has_day_ref = any(w in query_clean.split() or w in query_clean for w in [
        "today", "tomorrow", "tm", "tmrw", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
    ])
    has_time_ref = any(w in query_clean.split() or w in query_clean for w in [
        "am", "pm", "morning", "afternoon", "evening", "baje", "o'clock"
    ]) or bool(re.search(r"\b(1[0-2]|[1-9])(?::[0-5]\d|\s+[0-5]\d)?\s*(am|pm)?\b", query_clean))

    # Build Focused, Progressive MAI-Style Receptionist Response
    if kb_facts["matched_procedures"]:
        proc = kb_facts["matched_procedures"][0]
        doc = kb_facts["matched_doctors"][0] if kb_facts["matched_doctors"] else CLINIC_KB["doctors"][0]

        is_price_query = any(w in query_clean for w in ["cost", "price", "rate", "fee", "kharcha", "emi", "discount", "package", "how much"])
        is_doctor_query = any(w in query_clean for w in ["doctor", "dentist", "specialist", "who", "qualification", "experience"])

        if is_price_query:
            response_text = (
                f"Our {proc['name']} packages range between {proc['price_range_inr']}. "
                f"We also offer 0% interest EMI options starting at {proc['emi_starting']}.\n\n"
                f"Would you like me to check available consultation slots for you with {doc['name']}?"
            )
        elif is_doctor_query:
            response_text = (
                f"Our {proc['name']} consultations are led by {doc['name']} ({doc['title']}), "
                f"who has {doc['experience_years']} years of specialized experience.\n\n"
                f"Would you like me to check available consultation slots for you this week?"
            )
        else:
            response_text = (
                f"For {proc['name']}, our consultations are led by {doc['name']}. "
                f"We have consultation slots available tomorrow:\n"
                f"• 10:30 AM\n"
                f"• 04:00 PM\n\n"
                f"Which time works best for you?"
            )

    elif kb_facts["matched_faqs"]:
        faq = kb_facts["matched_faqs"][0]
        response_text = (
            f"{faq['answer']}\n\n"
            f"Would you like me to check available consultation slots for you at our Koramangala clinic?"
        )
    elif has_day_ref or has_time_ref:
        is_valid_time, invalid_time_str = check_operating_hours_validity(query_clean)
        if not is_valid_time:
            response_text = (
                f"⚠️ Our clinic operating hours are Monday to Saturday from 9:00 AM to 8:00 PM (and Sunday 10:00 AM to 2:00 PM).\n\n"
                f"*{invalid_time_str}* is outside our operating hours.\n\n"
                f"Available consultation slots tomorrow include:\n"
                f"• 10:30 AM\n"
                f"• 11:30 AM\n"
                f"• 04:00 PM\n"
                f"• 06:30 PM\n\n"
                f"Please let us know which of these times works best for you!"
            )
        else:
            response_text = (
                f"Great choice{name_greeting}! I can hold that time for you. 😊\n\n"
                f"Doctor: Dr. Chinmay Hudedamani\n"
                f"Location: Apex Dental Center, Koramangala, Bengaluru\n\n"
                f"To secure this slot, could you please provide your 10-digit registered mobile number?"
            )
    elif is_slot_query:
        response_text = (
            "Our clinic is open Monday to Saturday from 9:00 AM to 8:00 PM, and Sunday from 10:00 AM to 2:00 PM.\n\n"
            "Which treatment are you looking to visit for (such as Invisalign clear aligners, dental implants, or a general checkup), and what time works best for you?"
        )
    else:
        response_text = (
            f"How can I help you today{name_greeting}? Feel free to ask about our dental treatments (Invisalign, Root Canal, Implants), pricing, or booking a consultation at Apex Dental Center!"
        )

    return {
        "whatsapp_response": sanitize_llm_response(response_text),
        "grounding_facts": kb_facts
    }
