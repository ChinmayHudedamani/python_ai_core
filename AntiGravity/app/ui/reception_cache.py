# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI / Copus AI — Offline-First Receptionist Desk Cache & On-the-Spot Payment Collector

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass(slots=True)
class OfflineAppointmentRecord:
    """Memory-optimized slots-backed appointment record for reception desk payment & check-in."""
    checkin_code: str
    patient_name: str
    patient_phone: str
    procedure: str
    slot_time_ist: str = "10:00 AM IST"
    slot_time_iso: Optional[str] = None
    amount_due_inr: int = 700
    is_verified: bool = False
    payment_status: str = "PENDING_AT_DESK"  # PENDING_AT_DESK -> PAID_AT_DESK


class ReceptionistDailyCache:
    """Offline-First Receptionist Desk Cache & On-the-Spot Payment Collector."""

    def __init__(self) -> None:
        self._roster_cache: Dict[str, OfflineAppointmentRecord] = {}

    def seed_daily_roster(self, records: Dict[str, OfflineAppointmentRecord]) -> None:
        """Pulls and caches the active day's roster into memory/session state."""
        self._roster_cache = records

    def verify_checkin_code(self, checkin_code: str) -> Dict[str, str]:
        """Legacy helper delegating to verify_and_collect_payment."""
        return self.verify_and_collect_payment(checkin_code, payment_method="UPI")

    def verify_and_collect_payment(
        self, checkin_code: str, payment_method: str = "UPI"
    ) -> Dict[str, str]:
        """Verifies arriving patient and registers on-the-spot payment at reception."""
        sanitized_code = checkin_code.strip().upper()
        record = self._roster_cache.get(sanitized_code)

        if not record:
            return {
                "status": "NOT_FOUND",
                "message": f"❌ Code '{sanitized_code}' not found in today's local roster cache."
            }

        if record.is_verified:
            return {
                "status": "ALREADY_VERIFIED",
                "message": f"⚠️ Code '{sanitized_code}' was already checked in for patient {record.patient_name}. Payment Status: {record.payment_status}."
            }

        record.is_verified = True
        record.payment_status = f"PAID_AT_DESK ({payment_method})"

        return {
            "status": "SUCCESS",
            "message": (
                f"✅ **CHECK-IN SUCCESSFUL!**\n"
                f"👤 **Patient**: {record.patient_name}\n"
                f"🦷 **Procedure**: {record.procedure}\n"
                f"🕒 **Slot**: {record.slot_time_ist}\n"
                f"💰 **Payment Collected**: ₹{record.amount_due_inr} via {payment_method}"
            )
        }


# Default Mock Roster for Streamlit Reception Dashboard
DEFAULT_MOCK_ROSTER: List[Dict[str, Any]] = [
    {"code": "APX-4928", "name": "Rahul Sharma", "time": "10:30 AM IST", "symptom": "Lower Molar Toothache", "status": "CONFIRMED"},
    {"code": "APX-8237", "name": "Priya Nair", "time": "11:15 AM IST", "symptom": "Teeth Whitening Consult", "status": "CHECKED_IN"},
    {"code": "APX-3912", "name": "Ananya Roy", "time": "02:00 PM IST", "symptom": "Crown Replacement", "status": "SLOT_HELD"},
    {"code": "APX-9102", "name": "Vikram Seth", "time": "04:30 PM IST", "symptom": "Wisdom Tooth Extraction", "status": "CONFIRMED"},
]


# Backward compatibility helper
def verify_checkin_code_offline(checkin_code: str, roster_cache: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    cache = ReceptionistDailyCache()
    mock_records: Dict[str, OfflineAppointmentRecord] = {
        item["code"]: OfflineAppointmentRecord(
            checkin_code=item["code"],
            patient_name=item["name"],
            patient_phone="+919876543210",
            procedure=item["symptom"],
            slot_time_ist=item["time"],
            is_verified=(item["status"] == "CHECKED_IN")
        )
        for item in (roster_cache or DEFAULT_MOCK_ROSTER)
    }
    cache.seed_daily_roster(mock_records)
    res = cache.verify_and_collect_payment(checkin_code)

    return {
        "verified": (res["status"] == "SUCCESS"),
        "offline_fallback": True,
        "patient_name": mock_records.get(checkin_code.strip().upper(), OfflineAppointmentRecord("", "Unknown", "", "", "")).patient_name,
        "appointment_time": mock_records.get(checkin_code.strip().upper(), OfflineAppointmentRecord("", "", "", "", "")).slot_time_ist,
        "symptom": mock_records.get(checkin_code.strip().upper(), OfflineAppointmentRecord("", "", "", "", "")).procedure,
        "status": res["status"],
        "message": res["message"]
    }
