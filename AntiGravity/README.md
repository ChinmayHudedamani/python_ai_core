# 🦷 APEX AI — Production Clinical Assistant & Doctor Command Center

APEX AI is an enterprise-grade, zero-hallucination WhatsApp Clinical Assistant built using the **AI Sandwich Architecture**: `Deterministic Ingress Filter` $\rightarrow$ `LLM JSON Extraction` $\rightarrow$ `Deterministic DB Lookup` $\rightarrow$ `LLM Synthesis` $\rightarrow$ `Deterministic Egress Filter`.

---

## 🏛️ Architectural Overview

```
                      ┌─────────────────────────────────────────┐
                      │   Meta WhatsApp Cloud API Webhook      │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │      Pre-Guardrail Sanitizer &          │
                      │      Multilingual Triage Engine         │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Phone-Based RBAC Persona Router      │
                      │  (Doctor Admin vs Patient Concierge)   │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    Redis Hashes Session State &         │
                      │    Ambiguity-Free Slot Cache            │
                      └────────────────────┬────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │    FastAPI Core / Postgres Engine /     │
                      │    SQLite SQLModel Knowledge Base       │
                      └─────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Local Demo

### 1. Installation
```bash
git clone https://github.com/ChinmayHudedamani/python_ai_core.git
cd python_ai_core
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Seed Relational Knowledge Base
```bash
python scripts/seed_kb.py
```

### 3. Launch Streamlit Local Demo
```bash
streamlit run demo_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Automated Test Suite

Run the full suite of unit tests, RBAC authorizations, and the 50-client concurrency stress test:
```bash
python tests/test_stress.py
python test_phase1_infrastructure.py
```

---

## 📜 License
Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
