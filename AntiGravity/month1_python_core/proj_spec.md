# 🦷 PROJECT SPECIFICATION: Level 9.5 Dental Clinic Centaur Responder
**Target Deadline:** August 5th
**Developer Role:** Lead AI Engineer & Human-in-the-Loop (HITL) Account Executive
**Target Market:** Local Dental Clinics in Bengaluru (Currently using Pen & Paper / Excel)

---

## 1. CORE ARCHITECTURAL PHILOSOPHY
We are building a **Level 9.5 Centaur Architecture**—an Applied AI system that automates 90% of front-desk triage and data intake, but intentionally pauses and alerts a human closer for high-ticket sales or medical emergencies. 

**Zero-EMR Requirement:** The system must NOT force clinics to purchase cloud EMR software. It must log all patient data into a local CSV/Excel spreadsheet (`appointments_ledger.csv`) that clinic receptionists can open on their desktop.

---

## 2. THE 7-DAY DEVELOPMENT SPRINT
* **Day 1 (Completed):** System Architecture, Business Blueprint & IDE Setup.
* **Day 2 (Current Focus):** String Sanitization & JSON Payload Formatting (`clean_client_data`).
* **Day 3:** Gemini API Integration & The 1-100 Lead Intent Scorer.
* **Day 4:** Zero-Hallucination RAG (Injecting clinic price lists & FAQ PDFs).
* **Day 5:** Automated CSV/Excel Offline Ledger Writer.
* **Day 6:** Safety Circuit Breakers (112 Medical Emergency Override & HITL hand-off).
* **Day 7:** The Adversarial Crucible (Stress-testing typos, prompt injection, and edge cases).

---

## 3. TECHNICAL SPECIFICATIONS & MODULES

### Module A: Intake Valve (Day 2 Data Cleaner)
* Must strip leading/trailing whitespace (`.strip()`), proper-case patient names (`.title()`), remove dashes/spaces from phone numbers, and uppercase procedure codes.
* Must package data into a structured Python dictionary and export as formatted JSON (`json.dumps(..., indent=2)`).

### Module B: The 112 Emergency Kill-Switch (Absolute Guardrail)
* Must scan incoming messages for emergency keywords: `["bleeding heavily", "can't breathe", "chest pain", "unconscious", "severe trauma", "syncope"]`.
* **Action:** Immediately bypass LLM text generation, output a hardcoded warning commanding the user to call **112 (National Emergency Number)**, and trigger an urgent SMS/WhatsApp siren to the clinic owner.

### Module C: VIP Revenue Scorer & Triage Analyzer
* Must identify high-ticket procedure interest: `["Implants", "Invisalign", "Aligners", "Smile Makeover", "Full Mouth Rehab", "Root Canal"]`.
* **Action:** If `is_high_ticket == True` and confidence >= 80%, flag as VIP, append to spreadsheet, pause automated replies, and send a priority WhatsApp alert to the human closer (AE) to call the patient within 15 minutes.