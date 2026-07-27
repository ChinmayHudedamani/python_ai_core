# 🦷 APEX AI — Yelahanka Node v0.2 AI Concierge

Production implementation of TrueLark **MIDGO (Mixed-Initiative Dialogues with Goal Orientation)** architecture paired with a **Deterministic 30-Intent Finite State Graph (FSG)** across 5 Macro-States for **Apex Dental Center & Implant Institute, Yelahanka Node v0.2**.

---

## 🏛️ Target Directory Architecture

```text
apex-node-yelahanka-v0.2/
├── app/
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── schemas.py          # Pydantic MIDGO dual-output & 30-intent taxonomy
│   │   └── llm_client.py       # Official google-genai structured JSON wrapper & telemetry logger
│   └── ui/
│       ├── __init__.py
│       └── demo_app.py         # Streamlit interface, top 5 fast-path buttons & telemetry sidebar
├── logs/
│   └── telemetry.jsonl         # Persistent failure and interaction audit trail log
├── .env.example                # Template for environment variables (GEMINI_API_KEY)
├── requirements.txt            # Pinned production dependencies
└── README.md                   # Technical documentation & architecture overview
```

---

## 🧠 Finite State Graph (FSG) & 30-Intent Taxonomy

The conversational agent operates across **5 Macro-States ($M_1 \dots M_5$)** and **30 intent taxonomy tags**:

1. **`M1_STATE_LOGISTICS`**: `INTENT_CONSULT_FEE`, `INTENT_HOURS_WEEKEND`, `INTENT_CLINIC_TIMINGS`, `INTENT_EMERGENCY_BOOKING`, `INTENT_LANGUAGE_SUPPORT`, `INTENT_PARKING_VALET`, `INTENT_TELE_DENTISTRY`, `INTENT_STERILIZATION_PROTOCOLS`
2. **`M2_STATE_FINANCE`**: `INTENT_INSURANCE_CLAIM`, `INTENT_EMI_PLANS`, `INTENT_COST_RCT`, `INTENT_COST_IMPLANTS`, `INTENT_WARRANTY_CARD`
3. **`M3_STATE_PREVENTIVE`**: `INTENT_SCALING_DURATION`, `INTENT_BLEEDING_GUMS`, `INTENT_TOOTH_SENSITIVITY`, `INTENT_DIAGNOSTIC_XRAY`, `INTENT_RCT_SITTINGS`
4. **`M4_STATE_COSMETIC_SURGICAL`**: `INTENT_TEETH_WHITENING`, `INTENT_ALIGNERS_BRACES`, `INTENT_ORTHODONTIC_COST`, `INTENT_WISDOM_EXTRACTION`, `INTENT_CROWNS_BRIDGES`, `INTENT_VENEERS_LIFESPAN`, `INTENT_BRIDGE_VS_IMPLANT`, `INTENT_DENTURES_ELDERLY`, `INTENT_LASER_DENTISTRY`, `INTENT_PEDIATRIC_DENTISTRY`
5. **`M5_STATE_EMERGENCY`**: 🚨 `INTENT_TRAUMA_FIRST_AID`, `INTENT_POST_OP_CARE`

---

## 🚨 Emergency Safety Exemption Rule

Any turn classified under `INTENT_TRAUMA_FIRST_AID` or `INTENT_EMERGENCY_BOOKING` immediately bypasses standard booking loops to deliver urgent clinical first-aid guidelines (e.g. pressure with clean gauze, tooth preservation in cold milk) and unlocks a priority emergency check-in code (`APX-EMERGENCY-XXXX`).

---

## 🚀 Execution & Launch

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_LLM_MODEL=gemini-2.5-flash
```

### 3. Launch Yelahanka Node Telemetry Hub
```bash
streamlit run app/ui/demo_app.py
```
*(Or run `streamlit run app.py`)*

Open [http://localhost:8504](http://localhost:8504) in your browser.

---

## 📜 License & Ownership
Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
