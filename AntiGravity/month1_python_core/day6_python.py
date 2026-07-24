import json
import os
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from day2_python import clean_client_data, mask_pii
from day4_python import generate_zero_hallucination_response
from day5_python import OfflineLedgerWriter

ALERTS_DIR: Path = Path(__file__).parent / "alerts"
QUEUED_DIR: Path = Path(__file__).parent / "alerts" / "queued_morning"

def ensure_alerts_directories() -> None:
    """Ensures alert output directories exist for immediate and quiet-hour queued logs."""
    ALERTS_DIR.mkdir(parents=True, exist_ok=True)
    QUEUED_DIR.mkdir(parents=True, exist_ok=True)


def is_within_operating_callback_hours(now: Optional[datetime.datetime] = None) -> bool:
    """
    Evaluates whether system local time is within normal doctor callback hours (8:00 AM - 9:00 PM).
    Prevents waking senior specialists at 2:00 AM for non-emergency lead inquiries.
    """
    current_dt: datetime.datetime = now or datetime.datetime.now()
    current_hour: int = current_dt.hour
    return 8 <= current_hour < 21


class SafetyCircuitBreaker:
    """
    Enterprise Time-Aware Safety Circuit Breaker & Pre-Qualified VIP Dispatcher.
    - Medical Emergency (ESI RED): 24/7 112 National Emergency Referral & Immediate File Dispatch.
    - VIP High-Revenue Leads: Immediate 15-Min Dispatch during daytime (8 AM - 9 PM),
      Idempotent Morning Queueing (8 AM) during quiet night hours (9 PM - 8 AM).
    """

    def __init__(self, ledger_writer: Optional[OfflineLedgerWriter] = None):
        ensure_alerts_directories()
        self.ledger: OfflineLedgerWriter = ledger_writer or OfflineLedgerWriter()

    def process_intake_safety_circuit(self, raw_patient_data: Dict[str, Any], current_time_override: Optional[datetime.datetime] = None, is_followup: bool = False) -> Dict[str, Any]:
        """
        Executes Advanced Safety Circuit & Quiet-Hour Time-Aware VIP Hand-off:
        1. RAG & Threat Inspection (Day 4 Security Shield)
        2. ESI RED Medical Emergency Override (24/7 Dispatch)
        3. Pre-Qualified VIP Lead Dispatch (Time-Aware: Daytime 15-min SLA vs Nighttime 8-AM Queue)
        4. Idempotent Offline CSV Ledger Recording (Day 5)
        """
        response: Dict[str, Any] = generate_zero_hallucination_response(raw_patient_data, is_followup=is_followup)
        triage: Dict[str, Any] = response.get("triage", {})
        lead_tier: str = triage.get("lead_tier", "COLD_ROUTINE")
        patient: Dict[str, Any] = response.get("patient", {})

        now_dt: datetime.datetime = current_time_override or datetime.datetime.now()
        timestamp_str: str = now_dt.strftime("%Y%m%d_%H%M%S_%f")
        is_daytime: bool = is_within_operating_callback_hours(now_dt)

        circuit_status: Dict[str, Any] = {
            "circuit_action": "STANDARD_AUTOMATED_REPLY",
            "alert_file": None,
            "hitl_required": False,
            "callback_window": "STANDARD_RECEPTION"
        }

        # 1. Tier 1: Medical Emergency Override (24/7 ESI RED)
        if lead_tier == "RED_CRITICAL_EMERGENCY":
            alert_path = ALERTS_DIR / f"EMERGENCY_ALERT_{timestamp_str}.json"
            alert_payload = {
                "alert_type": "MEDICAL_EMERGENCY_ESI_RED",
                "severity": "CRITICAL_24_7",
                "patient_name": patient.get("name", "Unknown"),
                "phone": patient.get("phone", ""),
                "masked_phone": mask_pii(patient.get("phone", "")),
                "notes": patient.get("notes", ""),
                "action_required": "IMMEDIATE 112 EMERGENCY CALL / VISIT ER",
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
            with open(alert_path, "w", encoding="utf-8") as f:
                json.dump(alert_payload, f, indent=2)

            circuit_status["circuit_action"] = "CRITICAL_112_OVERRIDE_TRIGGERED"
            circuit_status["alert_file"] = str(alert_path)
            circuit_status["hitl_required"] = True
            circuit_status["callback_window"] = "IMMEDIATE_24_7_EMERGENCY"

        # 2. Tier 2: VIP High-Revenue Leads (Time-Aware Quiet Hours Guard)
        elif lead_tier == "VIP_HIGH_REVENUE":
            grounding: Dict[str, Any] = response.get("grounding_facts", {})
            doctors: List[str] = grounding.get("matched_doctors", ["Dr. Chinmay Hudedamani"])
            assigned_doctor: str = doctors[0] if doctors else "Dr. Chinmay Hudedamani"

            if is_daytime:
                # Daytime: Immediate 15-Minute HITL Alert
                alert_path = ALERTS_DIR / f"VIP_HITL_ALERT_{timestamp_str}.json"
                action_type = "VIP_15MIN_HITL_DISPATCH_TRIGGERED"
                callback_sla = "Immediate 15-Minute Human Callback Window"
            else:
                # Quiet Night Hours (9 PM - 8 AM): Queue for 8 AM Morning Dispatch without disturbing doctor at 2 AM
                alert_path = QUEUED_DIR / f"VIP_QUEUED_MORNING_{timestamp_str}.json"
                action_type = "VIP_QUEUED_FOR_MORNING_CALLBACK"
                callback_sla = "Queued for Priority 8:00 AM Morning Callback (Quiet Hours Protection)"

                # Soften WhatsApp text for late-night inquiries
                orig_msg = response.get("whatsapp_response", "")
                night_note = "\n\n🌙 *Late Night Inquiry Note*: Our clinic is currently closed for the night. Our Senior Specialist team has queued your inquiry for priority 8:30 AM morning callback!"
                response["whatsapp_response"] = orig_msg + night_note

            alert_payload = {
                "alert_type": action_type,
                "severity": "HIGH_PRIORITY_REVENUE",
                "quiet_hours_active": not is_daytime,
                "patient_name": patient.get("name", "Unknown"),
                "phone": patient.get("phone", ""),
                "masked_phone": mask_pii(patient.get("phone", "")),
                "procedure_code": patient.get("procedure_code", "N/A"),
                "intent_score": triage.get("intent_score", 100),
                "assigned_doctor": assigned_doctor,
                "target_sla": callback_sla,
                "available_slots": grounding.get("available_slots", []),
                "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

            with open(alert_path, "w", encoding="utf-8") as f:
                json.dump(alert_payload, f, indent=2)

            circuit_status["circuit_action"] = action_type
            circuit_status["alert_file"] = str(alert_path)
            circuit_status["hitl_required"] = True
            circuit_status["callback_window"] = callback_sla

        # 3. Record in Offline Ledger
        ledger_result = self.ledger.log_patient_intake(response)
        response["circuit_status"] = circuit_status
        response["ledger_result"] = ledger_result

        return response


if __name__ == "__main__":
    print("==================================================")
    print("   DAY 6: TIME-AWARE QUIET HOURS & SAFETY DEMO")
    print("==================================================\n")

    breaker = SafetyCircuitBreaker()

    # Daytime test (2:00 PM)
    day_time = datetime.datetime.now().replace(hour=14, minute=0)
    # Nighttime test (2:00 AM)
    night_time = datetime.datetime.now().replace(hour=2, minute=0)

    sample_vip = {
        "name": "Ananya Roy",
        "phone": "+919988776655",
        "procedure_code": "ALIGNERS",
        "notes": "Hi, what is the cost of invislin clear aligners in Bengaluru? Do you have EMI options?"
    }

    print("--- DAYTIME VIP INQUIRY (2:00 PM) ---")
    res_day = breaker.process_intake_safety_circuit(sample_vip, current_time_override=day_time)
    print(json.dumps(res_day["circuit_status"], indent=2))

    print("\n--- NIGHTTIME VIP INQUIRY (2:00 AM - QUIET HOURS GUARD) ---")
    res_night = breaker.process_intake_safety_circuit(sample_vip, current_time_override=night_time)
    print(json.dumps(res_night["circuit_status"], indent=2))
