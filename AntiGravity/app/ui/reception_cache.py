# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# Copus AI / APEX AI — Offline-First Receptionist Local Cache Engine

from typing import Dict, Any, List

DEFAULT_MOCK_ROSTER: List[Dict[str, Any]] = [
    {"code": "APX-4928", "name": "Rahul Sharma", "time": "10:30 AM", "symptom": "Lower Molar Toothache", "status": "CONFIRMED"},
    {"code": "APX-8237", "name": "Priya Nair", "time": "11:15 AM", "symptom": "Teeth Whitening Consult", "status": "CHECKED_IN"},
    {"code": "APX-3912", "name": "Ananya Roy", "time": "02:00 PM", "symptom": "Crown Replacement", "status": "SLOT_HELD"},
    {"code": "APX-9102", "name": "Vikram Seth", "time": "04:30 PM", "symptom": "Wisdom Tooth Extraction", "status": "CONFIRMED"},
]


def verify_checkin_code_offline(checkin_code: str, roster_cache: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Verifies Check-In Code (APX-XXXX) against local daily_roster_cache:
    - Provides zero-latency verification even if primary DB queries fail or timeout.
    """
    cache = roster_cache or DEFAULT_MOCK_ROSTER
    query_code = checkin_code.strip().upper()

    for item in cache:
        if item["code"].upper() == query_code:
            return {
                "verified": True,
                "offline_fallback": True,
                "patient_name": item["name"],
                "appointment_time": item["time"],
                "symptom": item["symptom"],
                "status": "CHECKED_IN",
                "message": f"✅ Code {query_code} Verified! Patient: {item['name']} ({item['time']}) marked CHECKED_IN."
            }

    return {
        "verified": False,
        "offline_fallback": True,
        "message": f"⚠️ Check-In Code '{query_code}' not found in local offline roster cache."
    }
